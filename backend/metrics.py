"""
metrics.py — Compute and format RL performance metrics.

Provides utilities to:
  - Compute per-step average rewards
  - Compute cumulative regret
  - Compare multiple agents side-by-side
  - Generate Plotly-compatible chart data (returned as JSON-safe dicts)
"""

import numpy as np
from typing import List, Dict, Any


# ---------------------------------------------------------------------------
# Core metric functions
# ---------------------------------------------------------------------------

def compute_average_rewards(reward_history: List[float]) -> List[float]:
    """
    Running average of rewards over time.
    avg_reward[t] = mean(rewards[0 .. t])
    """
    if not reward_history:
        return []
    cumsum = np.cumsum(reward_history)
    return (cumsum / (np.arange(len(reward_history)) + 1)).tolist()


def compute_cumulative_regret(
    reward_history: List[float],
    optimal_reward: float = 2.0,
) -> List[float]:
    """
    Cumulative regret over time.
    regret[t] = sum_{i=0}^{t} (optimal - reward[i])
    """
    if not reward_history:
        return []
    per_step = [optimal_reward - r for r in reward_history]
    return np.cumsum(per_step).tolist()


def compute_cumulative_rewards(reward_history: List[float]) -> List[float]:
    """Cumulative sum of rewards."""
    if not reward_history:
        return []
    return np.cumsum(reward_history).tolist()


# ---------------------------------------------------------------------------
# Plotly chart data generators
# ---------------------------------------------------------------------------

def reward_curve_chart(
    agents: Dict[str, List[float]],
) -> Dict[str, Any]:
    """
    Build Plotly trace data for the average-reward curve.

    Parameters
    ----------
    agents : dict mapping agent name → reward_history list

    Returns
    -------
    Plotly-compatible figure dict (traces + layout)
    """
    traces = []
    colours = {
        "epsilon_greedy": "#39ff14",   # neon green
        "ucb": "#bf5fff",              # electric purple
    }

    for name, history in agents.items():
        avg = compute_average_rewards(history)
        traces.append({
            "type": "scatter",
            "mode": "lines",
            "name": name.replace("_", "-"),
            "x": list(range(1, len(avg) + 1)),
            "y": avg,
            "line": {
                "color": colours.get(name, "#00e5ff"),
                "width": 2,
            },
        })

    return {
        "data": traces,
        "layout": {
            "title": "Average Reward Over Time",
            "xaxis": {"title": "Step", "color": "#aaa"},
            "yaxis": {"title": "Avg Reward", "color": "#aaa"},
            "paper_bgcolor": "#0d0d0d",
            "plot_bgcolor": "#0d0d0d",
            "font": {"color": "#e0e0e0", "family": "Inter, sans-serif"},
            "legend": {"orientation": "h"},
        },
    }


def regret_curve_chart(
    agents: Dict[str, List[float]],
    optimal_reward: float = 2.0,
) -> Dict[str, Any]:
    """
    Build Plotly trace data for the cumulative-regret curve.
    """
    traces = []
    colours = {
        "epsilon_greedy": "#39ff14",
        "ucb": "#bf5fff",
    }

    for name, history in agents.items():
        regret = compute_cumulative_regret(history, optimal_reward)
        traces.append({
            "type": "scatter",
            "mode": "lines",
            "name": name.replace("_", "-"),
            "x": list(range(1, len(regret) + 1)),
            "y": regret,
            "line": {
                "color": colours.get(name, "#00e5ff"),
                "width": 2,
            },
        })

    return {
        "data": traces,
        "layout": {
            "title": "Cumulative Regret Over Time",
            "xaxis": {"title": "Step", "color": "#aaa"},
            "yaxis": {"title": "Cumulative Regret", "color": "#aaa"},
            "paper_bgcolor": "#0d0d0d",
            "plot_bgcolor": "#0d0d0d",
            "font": {"color": "#e0e0e0", "family": "Inter, sans-serif"},
            "legend": {"orientation": "h"},
        },
    }


def algorithm_comparison_chart(
    agents: Dict[str, List[float]],
) -> Dict[str, Any]:
    """
    Bar chart comparing final average reward per algorithm.
    """
    names = []
    final_avgs = []
    colours_list = []
    colour_map = {
        "epsilon_greedy": "#39ff14",
        "ucb": "#bf5fff",
    }

    for name, history in agents.items():
        avg = compute_average_rewards(history)
        names.append(name.replace("_", "-"))
        final_avgs.append(round(avg[-1], 4) if avg else 0.0)
        colours_list.append(colour_map.get(name, "#00e5ff"))

    return {
        "data": [
            {
                "type": "bar",
                "x": names,
                "y": final_avgs,
                "marker": {"color": colours_list},
            }
        ],
        "layout": {
            "title": "Algorithm Comparison (Final Avg Reward)",
            "xaxis": {"title": "Algorithm", "color": "#aaa"},
            "yaxis": {"title": "Final Avg Reward", "color": "#aaa"},
            "paper_bgcolor": "#0d0d0d",
            "plot_bgcolor": "#0d0d0d",
            "font": {"color": "#e0e0e0", "family": "Inter, sans-serif"},
        },
    }


# ---------------------------------------------------------------------------
# Summary stats
# ---------------------------------------------------------------------------

def summary_stats(reward_history: List[float]) -> Dict[str, float]:
    if not reward_history:
        return {}
    arr = np.array(reward_history)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "min": float(arr.min()),
        "max": float(arr.max()),
        "total": float(arr.sum()),
        "n": len(reward_history),
    }
