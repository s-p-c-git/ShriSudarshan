"""FinRL Trading Environment.

Custom Gymnasium environment for trade execution.
State space is augmented with semantic embeddings from R1/Janus.
"""

import logging
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces


logger = logging.getLogger(__name__)


class TradingEnvironment(gym.Env):
    """
    Trading Environment for RL-based execution.

    State Space:
        - Price features (normalized)
        - Technical indicators
        - R1 sentiment signal
        - Janus pattern confidence
        - Strategy direction
        - Combined signal

    Action Space:
        - Continuous: amount to buy (positive) or sell (negative)

    Reward:
        - P&L from action + penalties for risk
    """

    def __init__(
        self,
        initial_balance: float = 100000.0,
        transaction_cost: float = 0.001,
    ):
        """
        Initialize trading environment.

        Args:
            initial_balance: Starting portfolio value
            transaction_cost: Cost per transaction (percentage)
        """
        super().__init__()

        self.initial_balance = initial_balance
        self.transaction_cost = transaction_cost

        # State space: 9 features
        # [price, rsi_norm, macd, r1_signal, janus_conf, strategy_dir, combined, spread, volume]
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(9,),
            dtype=np.float32,
        )

        # Action space: continuous [-1, 1] representing sell to buy
        self.action_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(1,),
            dtype=np.float32,
        )

        # Reset to initial state
        self.reset()

    def reset(
        self,
        seed: int | None = None,
        options: dict | None = None,
    ) -> tuple[np.ndarray, dict]:
        """
        Reset environment to initial state.

        Returns:
            Initial observation and info dict
        """
        super().reset(seed=seed)

        self.balance = self.initial_balance
        self.position = 0.0
        self.current_price = 100.0
        self.step_count = 0

        # Initial state (neutral market)
        self.state = np.zeros(9, dtype=np.float32)
        self.state[0] = self.current_price

        return self.state, {}

    def step(
        self, action: np.ndarray
    ) -> tuple[np.ndarray, float, bool, bool, dict]:
        """
        Execute action and return new state.

        Args:
            action: Trading action [-1, 1]

        Returns:
            Tuple of (observation, reward, terminated, truncated, info)
        """
        action_value = float(action[0])

        # Calculate position change
        max_position_change = self.balance * 0.1 / self.current_price
        position_change = action_value * max_position_change

        # Apply transaction costs
        trade_cost = abs(position_change) * self.current_price * self.transaction_cost

        # Update position and balance
        self.position += position_change
        self.balance -= trade_cost

        # Simulate price movement (for training)
        # In production, this would come from market data
        price_change = np.random.normal(0, 0.02) * self.current_price
        self.current_price += price_change

        # Calculate reward
        pnl = self.position * price_change
        reward = pnl - trade_cost

        # Normalize reward
        reward = reward / self.initial_balance * 100

        # Update state
        self._update_state()

        self.step_count += 1

        # Episode ends after 1000 steps
        terminated = self.step_count >= 1000
        truncated = False

        info = {
            "balance": self.balance,
            "position": self.position,
            "price": self.current_price,
            "pnl": pnl,
        }

        return self.state, reward, terminated, truncated, info

    def _update_state(self):
        """Update state vector with current market conditions."""
        # Mock state update for training
        # In production, this would use real market data
        self.state[0] = self.current_price
        self.state[1] = np.random.uniform(-1, 1)  # RSI normalized
        self.state[2] = np.random.uniform(-0.1, 0.1)  # MACD
        self.state[3] = np.random.uniform(-1, 1)  # R1 sentiment
        self.state[4] = np.random.uniform(0, 1)  # Janus confidence
        self.state[5] = np.sign(self.position)  # Strategy direction
        self.state[6] = np.mean(self.state[1:6])  # Combined signal
        self.state[7] = np.random.uniform(0.01, 0.1)  # Spread
        self.state[8] = np.random.uniform(0.5, 2.0)  # Volume (normalized)

    def render(self):
        """Render environment state."""
        print(f"Step: {self.step_count}")
        print(f"Price: ${self.current_price:.2f}")
        print(f"Position: {self.position:.2f}")
        print(f"Balance: ${self.balance:.2f}")
