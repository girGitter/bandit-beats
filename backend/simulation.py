"""
simulation.py — Probabilistic user-behaviour simulator.

The simulator mimics how a real user would respond to a song
recommendation given their current context (mood, activity, time).

Each song has a set of "preferred_contexts".  When the recommended
song matches the user's context well, the probability of a positive
reaction (play / replay) is high; mismatches lead to skips.

Reward scheme
-------------
  listen  → +1.0
  replay  → +2.0
  skip    → -1.0
"""

import numpy as np
from typing import Dict, List, Any


# ---------------------------------------------------------------------------
# Context-to-song affinity scorer
# ---------------------------------------------------------------------------

def context_affinity(song: Dict[str, Any], context: Dict[str, str]) -> float:
    """
    Return a score in [0, 1] measuring how well a song fits the context.

    We compare each context dimension (mood, activity, time) against the
    song's preferred_contexts list and count the number of matches.
    """
    preferred = song.get("preferred_contexts", {})
    dimensions = ["mood", "activity", "time"]
    matches = sum(
        1
        for dim in dimensions
        if context.get(dim) in preferred.get(dim, [])
    )
    return matches / len(dimensions)


# ---------------------------------------------------------------------------
# Reaction probabilities
# ---------------------------------------------------------------------------

def reaction_probabilities(affinity: float) -> Dict[str, float]:
    """
    Map an affinity score to reaction probabilities.

    High affinity  → likely to replay or play
    Low affinity   → likely to skip
    """
    # Linear interpolation between "bad match" and "perfect match"
    p_listen = 0.20 + 0.50 * affinity   # [0.20, 0.70]
    p_replay = 0.05 + 0.40 * affinity   # [0.05, 0.45]
    p_skip = max(0.0, 1.0 - p_listen - p_replay)

    # Normalise just in case
    total = p_listen + p_replay + p_skip
    return {
        "listen": p_listen / total,
        "replay": p_replay / total,
        "skip":   p_skip   / total,
    }


# ---------------------------------------------------------------------------
# Reward mapping
# ---------------------------------------------------------------------------

REWARD_MAP = {
    "listen": 1.0,
    "replay": 2.0,
    "skip":  -1.0,
}


def simulate_reaction(
    song: Dict[str, Any],
    context: Dict[str, str],
    rng: np.random.Generator = None,
) -> tuple[str, float]:
    """
    Simulate a user reaction to a song in the given context.

    Returns
    -------
    reaction : str   — 'listen', 'replay', or 'skip'
    reward   : float — numeric reward signal
    """
    if rng is None:
        rng = np.random.default_rng()

    affinity = context_affinity(song, context)
    probs = reaction_probabilities(affinity)

    reaction = rng.choice(
        list(probs.keys()),
        p=list(probs.values()),
    )
    reward = REWARD_MAP[reaction]
    return str(reaction), float(reward)


# ---------------------------------------------------------------------------
# Bulk simulation run (used for chart pre-computation)
# ---------------------------------------------------------------------------

def run_simulation(
    agent,
    songs: List[Dict[str, Any]],
    contexts: List[Dict[str, str]],
    n_steps: int = 200,
    optimal_reward: float = 2.0,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Run `n_steps` interactions with the agent and return metrics.

    Parameters
    ----------
    agent         : BanditAgent subclass instance (will be reset first)
    songs         : list of song dicts from songs.json
    contexts      : list of context dicts to cycle through
    n_steps       : total simulation steps
    optimal_reward: reward we'd get if we always picked the best arm
    seed          : RNG seed for reproducibility

    Returns
    -------
    dict with keys: rewards, cumulative_rewards, avg_rewards, regrets
    """
    agent.reset()
    rng = np.random.default_rng(seed)

    rewards: List[float] = []
    cumulative_reward = 0.0
    cumulative_regret = 0.0
    regrets: List[float] = []
    cumulative_rewards: List[float] = []
    avg_rewards: List[float] = []

    for step in range(n_steps):
        context = contexts[step % len(contexts)]
        action = agent.select_action(context)
        song = songs[action]

        _, reward = simulate_reaction(song, context, rng)
        agent.update(action, reward)

        cumulative_reward += reward
        cumulative_regret += optimal_reward - reward

        rewards.append(reward)
        cumulative_rewards.append(cumulative_reward)
        avg_rewards.append(cumulative_reward / (step + 1))
        regrets.append(cumulative_regret)

        # Store regret in agent for external access
        agent.regret_history.append(cumulative_regret)

    return {
        "rewards": rewards,
        "cumulative_rewards": cumulative_rewards,
        "avg_rewards": avg_rewards,
        "regrets": regrets,
        "final_avg_reward": avg_rewards[-1] if avg_rewards else 0.0,
        "final_regret": regrets[-1] if regrets else 0.0,
    }
