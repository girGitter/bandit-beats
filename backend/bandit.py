"""
bandit.py — Base BanditAgent class for the Bandit-Beats RL system.

All reinforcement learning agents extend this base class.
It tracks Q-values (estimated reward per action), action counts,
and the full reward history — the core bookkeeping for any bandit.
"""

import numpy as np
from typing import List, Dict, Any


class BanditAgent:
    """
    Base multi-armed bandit agent.

    In our system:
        - Arms  = songs (each song is one "action")
        - State = context vector (mood, activity, time)
        - Reward = +1 (play), -1 (skip), +2 (replay)

    Subclasses override `select_action` with their exploration strategy.
    """

    def __init__(self, n_actions: int, song_ids: List[str]):
        """
        Args:
            n_actions: Total number of songs (arms).
            song_ids:  Ordered list of song IDs matching the action indices.
        """
        self.n_actions = n_actions
        self.song_ids = song_ids

        # Q[a] = running average reward for action a
        self.Q = np.zeros(n_actions, dtype=float)

        # N[a] = number of times action a has been selected
        self.N = np.zeros(n_actions, dtype=int)

        # Full history for plotting
        self.reward_history: List[float] = []
        self.action_history: List[int] = []

        # Cumulative regret over time (populated by simulation)
        self.regret_history: List[float] = []

        self.total_steps = 0

    # ------------------------------------------------------------------
    # Action selection — override in subclass
    # ------------------------------------------------------------------

    def select_action(self, context: Dict[str, Any]) -> int:  # pragma: no cover
        """
        Choose an action (song index) given the current context.
        Subclasses implement the exploration strategy here.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Value update (incremental mean update rule)
    # ------------------------------------------------------------------

    def update(self, action: int, reward: float) -> None:
        """
        Update the Q-value for `action` using the incremental mean:
            Q[a] ← Q[a] + (1/N[a]) * (reward − Q[a])

        This is equivalent to a sample mean but computed online.
        """
        self.N[action] += 1
        # Incremental mean: no need to store all past rewards
        self.Q[action] += (reward - self.Q[action]) / self.N[action]

        self.reward_history.append(reward)
        self.action_history.append(action)
        self.total_steps += 1

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get_state(self) -> Dict[str, Any]:
        """Return a serialisable snapshot of the agent state."""
        return {
            "q_values": self.Q.tolist(),
            "action_counts": self.N.tolist(),
            "total_steps": self.total_steps,
            "song_ids": self.song_ids,
        }

    def get_song_id(self, action: int) -> str:
        """Convert an action index to the corresponding song ID."""
        return self.song_ids[action]

    def get_action_index(self, song_id: str) -> int:
        """Convert a song ID to its action index."""
        return self.song_ids.index(song_id)

    def average_reward(self) -> float:
        """Mean reward across all interactions so far."""
        if not self.reward_history:
            return 0.0
        return float(np.mean(self.reward_history))

    def reset(self) -> None:
        """Reset all learned values — useful for fresh simulations."""
        self.Q = np.zeros(self.n_actions, dtype=float)
        self.N = np.zeros(self.n_actions, dtype=int)
        self.reward_history = []
        self.action_history = []
        self.regret_history = []
        self.total_steps = 0
