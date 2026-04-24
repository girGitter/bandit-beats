"""
ucb.py — Upper Confidence Bound (UCB1) bandit agent.

Exploration strategy:
  For each action a, compute an upper confidence bound:

      UCB(a) = Q[a] + c * sqrt( ln(t) / N[a] )

  where:
    Q[a]  = estimated mean reward for action a
    t     = total number of steps taken so far
    N[a]  = number of times action a has been selected
    c     = exploration constant (higher → more exploration)

  The agent always selects the action with the highest UCB score.

Why it works:
  - Actions played rarely have large √(ln t / N[a]) → high UCB → explored.
  - Once well-explored, the UCB term shrinks and Q[a] dominates.
  - This gives a theoretically optimal balance of exploration/exploitation.
"""

import numpy as np
from typing import Dict, Any

from bandit import BanditAgent


class UCBAgent(BanditAgent):
    """
    UCB1 agent.

    Parameters
    ----------
    n_actions : int
        Number of songs (arms).
    song_ids : list[str]
        Song IDs in action-index order.
    c : float
        Exploration constant.  Typical values: 1.0 – 2.0.
        Higher values widen the confidence bounds → more exploration.
    """

    def __init__(self, n_actions: int, song_ids: list, c: float = 1.4):
        super().__init__(n_actions, song_ids)
        self.c = c
        self.name = "ucb"

    # ------------------------------------------------------------------

    def select_action(self, context: Dict[str, Any]) -> int:
        """
        Select the action with the highest UCB score.

        On the very first pass through all actions (N[a] == 0), we try
        each action once before applying the UCB formula — this is the
        standard "play each arm at least once" initialisation.
        """
        t = self.total_steps + 1  # avoid log(0)

        # Play untried actions first (UCB is undefined for N[a] == 0)
        untried = np.where(self.N == 0)[0]
        if len(untried) > 0:
            return int(untried[0])

        # Compute UCB scores for all actions
        exploration_bonus = self.c * np.sqrt(np.log(t) / self.N)
        ucb_scores = self.Q + exploration_bonus

        # Break ties randomly
        max_ucb = np.max(ucb_scores)
        top_actions = np.where(ucb_scores == max_ucb)[0]
        return int(np.random.choice(top_actions))

    # ------------------------------------------------------------------

    def get_state(self) -> Dict[str, Any]:
        state = super().get_state()
        state["c"] = self.c
        state["algorithm"] = "ucb"

        # Include current UCB scores if we have data
        if self.total_steps > 0:
            t = self.total_steps
            with np.errstate(divide="ignore", invalid="ignore"):
                bonus = np.where(
                    self.N > 0,
                    self.c * np.sqrt(np.log(t) / self.N),
                    np.inf,
                )
            state["ucb_scores"] = (self.Q + bonus).tolist()
        else:
            state["ucb_scores"] = [None] * self.n_actions

        return state
