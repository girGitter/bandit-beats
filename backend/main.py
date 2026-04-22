"""
main.py — FastAPI application for Bandit-Beats.

Endpoints
---------
GET  /songs                   — list all songs
GET  /recommend               — get a recommendation for a given context
POST /feedback                — submit user feedback (play/skip/replay)
GET  /state/{algorithm}       — agent internal state snapshot
GET  /metrics/charts          — Plotly chart data for all three graphs
GET  /metrics/simulate        — run a fresh simulation and return chart data
GET  /health                  — health check
"""

import json
import sys
import os
from pathlib import Path
from typing import Literal, Optional

import numpy as np
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Path setup — allow running directly or from project root
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))

from bandit import BanditAgent
from epsilon_greedy import EpsilonGreedyAgent
from ucb import UCBAgent
from simulation import run_simulation, simulate_reaction
from metrics import (
    reward_curve_chart,
    regret_curve_chart,
    algorithm_comparison_chart,
    summary_stats,
)

# ---------------------------------------------------------------------------
# Load song catalogue
# ---------------------------------------------------------------------------
DATA_PATH = Path(__file__).parent.parent / "data" / "songs.json"

with open(DATA_PATH, "r") as f:
    SONGS: list = json.load(f)

SONG_IDS = [s["id"] for s in SONGS]
SONG_MAP = {s["id"]: s for s in SONGS}
N_SONGS = len(SONGS)

# ---------------------------------------------------------------------------
# Initialise agents  (one global instance each — state persists per session)
# ---------------------------------------------------------------------------
eg_agent = EpsilonGreedyAgent(N_SONGS, SONG_IDS, epsilon=0.15)
ucb_agent = UCBAgent(N_SONGS, SONG_IDS, c=1.4)

AGENTS = {
    "epsilon_greedy": eg_agent,
    "ucb": ucb_agent,
}

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Bandit-Beats API",
    description="Context-Aware Music Recommendation via Multi-Armed Bandits",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------
AlgorithmName = Literal["epsilon_greedy", "ucb"]
MoodType = Literal["happy", "sad", "energetic"]
ActivityType = Literal["study", "gym", "relax"]
TimeType = Literal["morning", "evening", "night"]
ReactionType = Literal["listen", "skip", "replay"]


class FeedbackRequest(BaseModel):
    algorithm: AlgorithmName
    song_id: str
    reaction: ReactionType
    mood: MoodType
    activity: ActivityType
    time: TimeType


class RecommendResponse(BaseModel):
    algorithm: str
    song_id: str
    song: dict
    action_index: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "songs_loaded": N_SONGS}


@app.get("/songs")
def list_songs():
    """Return the full song catalogue."""
    return {"songs": SONGS}


@app.get("/recommend", response_model=RecommendResponse)
def recommend(
    algorithm: AlgorithmName = Query("epsilon_greedy"),
    mood: MoodType = Query("happy"),
    activity: ActivityType = Query("study"),
    time: TimeType = Query("morning"),
):
    """
    Return a recommended song for the given context using the chosen algorithm.

    The agent selects an action (song index) based on its current Q-values
    and the exploration policy.  The context is passed so context-aware
    agents can use it in future iterations.
    """
    agent = AGENTS[algorithm]
    context = {"mood": mood, "activity": activity, "time": time}
    action = agent.select_action(context)
    song_id = agent.get_song_id(action)
    song = SONG_MAP[song_id]

    return {
        "algorithm": algorithm,
        "song_id": song_id,
        "song": song,
        "action_index": action,
    }


@app.post("/feedback")
def feedback(body: FeedbackRequest):
    """
    Submit user feedback and update the agent's Q-values.

    Reward mapping:
      listen  → +1.0
      replay  → +2.0
      skip    → -1.0
    """
    reward_map = {"listen": 1.0, "replay": 2.0, "skip": -1.0}
    reward = reward_map[body.reaction]

    agent = AGENTS[body.algorithm]

    if body.song_id not in SONG_IDS:
        raise HTTPException(status_code=404, detail=f"Song {body.song_id} not found")

    action = agent.get_action_index(body.song_id)
    agent.update(action, reward)

    return {
        "song_id": body.song_id,
        "reaction": body.reaction,
        "reward": reward,
        "new_q_value": round(agent.Q[action], 4),
        "action_count": int(agent.N[action]),
        "total_steps": agent.total_steps,
        "average_reward": round(agent.average_reward(), 4),
    }


@app.get("/state/{algorithm}")
def agent_state(algorithm: AlgorithmName):
    """Return a snapshot of the agent's internal state."""
    agent = AGENTS[algorithm]
    state = agent.get_state()
    state["reward_history"] = agent.reward_history[-50:]  # last 50 for bandwidth
    return state


@app.get("/metrics/charts")
def metrics_charts():
    """
    Return Plotly-ready chart data for:
      - Average reward over time
      - Cumulative regret over time
      - Algorithm comparison bar chart
    """
    histories = {
        name: agent.reward_history
        for name, agent in AGENTS.items()
    }

    return {
        "reward_curve": reward_curve_chart(histories),
        "regret_curve": regret_curve_chart(histories),
        "comparison": algorithm_comparison_chart(histories),
        "stats": {
            name: summary_stats(agent.reward_history)
            for name, agent in AGENTS.items()
        },
    }


@app.get("/metrics/simulate")
def metrics_simulate(
    n_steps: int = Query(default=300, ge=50, le=2000),
    seed: int = Query(default=42),
):
    """
    Run a fresh simulation (resetting agents) and return chart data.
    Useful for the "comparison" view without manual interaction.
    """
    # Build a rotating set of diverse contexts for the simulation
    context_pool = [
        {"mood": "happy",     "activity": "study",  "time": "morning"},
        {"mood": "energetic", "activity": "gym",    "time": "evening"},
        {"mood": "sad",       "activity": "relax",  "time": "night"},
        {"mood": "happy",     "activity": "relax",  "time": "evening"},
        {"mood": "energetic", "activity": "study",  "time": "morning"},
        {"mood": "sad",       "activity": "study",  "time": "night"},
    ]

    # Fresh agents for a clean simulation
    fresh_eg = EpsilonGreedyAgent(N_SONGS, SONG_IDS, epsilon=0.15)
    fresh_ucb = UCBAgent(N_SONGS, SONG_IDS, c=1.4)

    sim_eg = run_simulation(fresh_eg, SONGS, context_pool, n_steps, seed=seed)
    sim_ucb = run_simulation(fresh_ucb, SONGS, context_pool, n_steps, seed=seed)

    histories = {
        "epsilon_greedy": fresh_eg.reward_history,
        "ucb": fresh_ucb.reward_history,
    }

    return {
        "n_steps": n_steps,
        "reward_curve": reward_curve_chart(histories),
        "regret_curve": regret_curve_chart(histories),
        "comparison": algorithm_comparison_chart(histories),
        "epsilon_greedy": {
            "final_avg_reward": sim_eg["final_avg_reward"],
            "final_regret": sim_eg["final_regret"],
        },
        "ucb": {
            "final_avg_reward": sim_ucb["final_avg_reward"],
            "final_regret": sim_ucb["final_regret"],
        },
    }
