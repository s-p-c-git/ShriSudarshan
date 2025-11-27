"""FinRL Agent Implementation.

Reinforcement learning agent for trade execution.
Supports PPO, DDPG, A2C, and TD3 algorithms.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

import numpy as np


logger = logging.getLogger(__name__)

# =============================================================================
# Trading Action Thresholds (shared between RL discretization and rule-based)
# =============================================================================
# These thresholds define the decision boundaries for discretizing continuous
# actions into discrete buy/sell/hold decisions. Values chosen based on:
# - Empirical testing showing 0.3 provides good balance between action frequency and signal quality
# - Symmetric thresholds for buy/sell to avoid directional bias
ACTION_BUY_THRESHOLD = 0.3   # Combined signal above this triggers buy
ACTION_SELL_THRESHOLD = -0.3  # Combined signal below this triggers sell


class RLAgent:
    """
    Reinforcement Learning Agent for trade execution.

    Supports multiple algorithms from stable-baselines3.
    State space is augmented with semantic embeddings from R1/Janus.
    """

    def __init__(
        self,
        agent_type: str = "ppo",
        policy_path: Optional[str] = None,
    ):
        """
        Initialize RL Agent.

        Args:
            agent_type: Algorithm type (ppo, ddpg, a2c, td3)
            policy_path: Optional path to pre-trained policy
        """
        self.agent_type = agent_type.lower()
        self.model = None
        self.env = None

        # Initialize environment and model
        self._init_environment()
        self._init_model(policy_path)

    def _init_environment(self):
        """Initialize trading environment."""
        try:
            from environment import TradingEnvironment

            self.env = TradingEnvironment()
            logger.info("Trading environment initialized")
        except ImportError:
            logger.warning("Environment not available, using mock mode")
            self.env = None

    def _init_model(self, policy_path: Optional[str] = None):
        """
        Initialize or load the RL model.

        Args:
            policy_path: Optional path to pre-trained policy
        """
        try:
            from stable_baselines3 import A2C, DDPG, PPO, TD3

            algorithm_map = {
                "ppo": PPO,
                "ddpg": DDPG,
                "a2c": A2C,
                "td3": TD3,
            }

            if self.agent_type not in algorithm_map:
                raise ValueError(f"Unknown agent type: {self.agent_type}")

            algorithm = algorithm_map[self.agent_type]

            if policy_path and Path(policy_path).exists():
                logger.info(f"Loading model from {policy_path}")
                self.model = algorithm.load(policy_path, env=self.env)
            elif self.env is not None:
                logger.info(f"Creating new {self.agent_type.upper()} model")
                self.model = algorithm("MlpPolicy", self.env, verbose=1)
            else:
                logger.warning("No environment available, model not initialized")
                self.model = None

        except ImportError as e:
            logger.warning(f"Could not load stable-baselines3: {e}")
            self.model = None

    def predict(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Predict action for given state.

        Args:
            state: State dictionary with market and signal data

        Returns:
            Dictionary with action, confidence, and details
        """
        if self.model is None:
            return self._rule_based_predict(state)

        try:
            # Convert state dict to observation array
            obs = self._state_to_observation(state)

            # Get action from model
            action, _states = self.model.predict(obs, deterministic=True)

            # Get action probabilities/confidence
            if hasattr(self.model, "policy"):
                confidence = self._get_action_confidence(obs, action)
            else:
                confidence = 0.6

            # Map continuous action to discrete (-1, 0, 1)
            discrete_action = self._discretize_action(action)

            return {
                "action": int(discrete_action),
                "confidence": float(confidence),
                "amount": float(abs(action[0]) if isinstance(action, np.ndarray) else 0),
                "timing": "immediate",
                "slippage_estimate": 0.01,
                "policy_output": {
                    "raw_action": action.tolist() if isinstance(action, np.ndarray) else action,
                },
            }

        except RuntimeError as e:
            logger.error(f"Prediction error: {e}")
            return self._rule_based_predict(state)

    def _state_to_observation(self, state: dict[str, Any]) -> np.ndarray:
        """
        Convert state dictionary to observation array.

        Args:
            state: State dictionary

        Returns:
            NumPy array for model input
        """
        # Extract relevant features
        features = [
            state.get("price", 0.0),
            state.get("rsi_normalized", 0.0),
            state.get("macd", 0.0),
            state.get("r1_sentiment", 0.0),
            state.get("janus_pattern_confidence", 0.0),
            state.get("strategy_direction", 0.0),
            state.get("combined_signal", 0.0),
            state.get("spread", 0.0),
            state.get("volume", 0.0) / 1e6,  # Normalize volume
        ]

        return np.array(features, dtype=np.float32)

    def _discretize_action(self, action: np.ndarray) -> int:
        """
        Discretize continuous action to -1, 0, or 1.

        Args:
            action: Continuous action from model

        Returns:
            Discrete action
        """
        if isinstance(action, np.ndarray):
            action_value = action[0]
        else:
            action_value = action

        if action_value > ACTION_BUY_THRESHOLD:
            return 1  # Buy
        elif action_value < ACTION_SELL_THRESHOLD:
            return -1  # Sell
        else:
            return 0  # Hold

    def _get_action_confidence(
        self, obs: np.ndarray, action: np.ndarray
    ) -> float:
        """
        Get confidence score for action.

        Args:
            obs: Observation
            action: Predicted action

        Returns:
            Confidence score (0-1)
        """
        try:
            # Get action distribution
            if hasattr(self.model.policy, "get_distribution"):
                dist = self.model.policy.get_distribution(obs)
                if hasattr(dist, "log_prob"):
                    log_prob = dist.log_prob(action)
                    confidence = np.exp(log_prob.mean().item())
                    return min(1.0, max(0.0, confidence))
        except (AttributeError, RuntimeError) as exc:
            # If the model's policy does not support confidence estimation, fall back to default.
            logger.warning(
                "Could not compute action confidence: %s. Using default value.",
                exc,
            )

        return 0.6

    def _rule_based_predict(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Rule-based prediction fallback.

        Args:
            state: State dictionary

        Returns:
            Prediction result
        """
        combined = state.get("combined_signal", 0.0)

        if combined > ACTION_BUY_THRESHOLD:
            action = 1
            confidence = min(1.0, 0.5 + abs(combined))
        elif combined < ACTION_SELL_THRESHOLD:
            action = -1
            confidence = min(1.0, 0.5 + abs(combined))
        else:
            action = 0
            confidence = 0.5

        return {
            "action": action,
            "confidence": confidence,
            "amount": abs(combined) * 100,
            "timing": "immediate",
            "slippage_estimate": 0.01,
            "policy_output": {"mode": "rule_based"},
        }

    def train(self, episodes: int = 100) -> dict[str, Any]:
        """
        Train the RL model.

        Args:
            episodes: Number of training episodes

        Returns:
            Training statistics
        """
        if self.model is None or self.env is None:
            raise RuntimeError("Model or environment not initialized")

        timesteps = episodes * 1000
        self.model.learn(total_timesteps=timesteps)

        return {
            "episodes": episodes,
            "timesteps": timesteps,
            "status": "completed",
        }

    def save(self, path: str):
        """Save model to path."""
        if self.model is None:
            raise RuntimeError("Model not initialized")

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.model.save(path)
        logger.info(f"Model saved to {path}")

    def load(self, path: str):
        """Load model from path."""
        self._init_model(path)
        logger.info(f"Model loaded from {path}")
