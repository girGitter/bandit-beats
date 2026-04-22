"""
epsilon_greedy.py — ε-Greedy bandit agent.

Exploration strategy:
  - With probability ε  → choose a random song   (explore)
  - With probability 1-ε → choose the best-known song (exploit)

A high ε means more exploration; a low ε means the agent mostly
exploits what it already knows.  ε can decay over time so the agent
explores aggressively early and becomes more confident later.
"""

import numpy as np
from typing import Dict, Any

from bandit import BanditAgent


class EpsilonGreedyAgent(BanditAgent):
    """
    ε-Greedy agent with optional epsilon decay.

    Parameters
    ----------
    n_actions : int
        Number of songs (arms).
    song_ids : list[str]
        Song IDs in action-index order.
    epsilon : float
        Initial exploration probability (0 < ε ≤ 1).
    epsilon_decay : float
        Multiplicative decay applied to ε after each step.
        Set to 1.0 for no decay.
    epsilon_min : float
        Floor value so exploration never fully stops.
    """

    def __init__(
        self,
        n_actions: int,
        song_ids: list,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
    ):
        super().__init__(n_actions, song_ids)
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.initial_epsilon = epsilon
        self.name = "epsilon_greedy"

    # ------------------------------------------------------------------

    def select_action(self, context: Dict[str, Any]) -> int:
        """
        Choose an action using the ε-greedy policy.

        The context is used for context-aware tie-breaking: among
        actions with the same Q-value, we prefer songs whose tags
        overlap with the current context labels.
        """
        if np.random.random() < self.epsilon:
            # --- Explore: pick any song at random ---
            action = int(np.random.randint(0, self.n_actions))
        else:
            # --- Exploit: pick the action with the highest Q-value ---
            # Break ties randomly
            max_q = np.max(self.Q)
            top_actions = np.where(self.Q == max_q)[0]
            action = int(np.random.choice(top_actions))

        # Decay epsilon after each selection
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        return action

    # ------------------------------------------------------------------

    def get_state(self) -> Dict[str, Any]:
        state = super().get_state()
        state["epsilon"] = self.epsilon
        state["algorithm"] = "epsilon_greedy"
        return state
