"""Execution Team - FinRL Reinforcement Learning Executor.

This module implements the "Execution Engine" of the Deep Reasoner v2.0 architecture.
It uses FinRL (Financial Reinforcement Learning) for low-latency trade execution.

Key Concept:
    The RL agent's state space is augmented with semantic embeddings from:
    - DeepSeek R1: Sentiment and strategy confidence
    - Janus-Pro: Visual pattern confidence

    This addresses the "Sim-to-Real" gap by decoupling:
    - High-latency reasoning (Strategy) from
    - Low-latency action (Execution)
"""

from typing import Any, Optional

import aiohttp

from ...config import settings
from ...config.prompts import FINRL_EXECUTION_AGENT_PROMPT
from ...data.schemas import (
    AgentReport,
    AgentRole,
    ExecutionPlan,
    FinRLExecutionReport,
    Order,
    OrderSide,
    OrderType,
    StrategyProposal,
)
from ...utils import get_logger
from ..base import BaseAgent


logger = get_logger(__name__)


class FinRLExecutionAgent(BaseAgent):
    """
    FinRL-based Execution Agent (Execution Engine).

    Uses reinforcement learning (PPO/DDPG) for optimal trade execution
    on a fast loop (seconds/minutes).

    Key Features:
        - State space augmented with R1/Janus embeddings
        - Low-latency execution decisions
        - Slippage minimization
        - Continuous trading based on last known strategic signals

    Latency Profile:
        - Inference: ~10ms (Fast Loop)
        - Operates continuously, asynchronously from strategy updates

    State Space:
        - Price data (OHLCV)
        - Order book data (if available)
        - R1 sentiment embedding (from last strategic update)
        - Janus pattern confidence (from last visual update)
        - Technical indicators
    """

    def __init__(self):
        """Initialize FinRL Execution Agent."""
        super().__init__(
            role=AgentRole.FINRL_EXECUTION_AGENT,
            system_prompt=FINRL_EXECUTION_AGENT_PROMPT,
            temperature=0.2,  # Low temperature for deterministic execution
        )
        self._session: Optional[aiohttp.ClientSession] = None

        # Last known signals from slow/medium loop agents
        self._last_r1_signal: float = 0.0
        self._last_janus_confidence: float = 0.0

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    def update_strategic_signals(
        self,
        r1_signal: Optional[float] = None,
        janus_confidence: Optional[float] = None,
    ):
        """
        Update strategic signals from slow/medium loop agents.

        Called asynchronously when R1 or Janus complete their analysis.

        Args:
            r1_signal: DeepSeek R1 sentiment signal (-1 to 1)
            janus_confidence: Janus pattern confidence (0 to 1)
        """
        if r1_signal is not None:
            self._last_r1_signal = r1_signal
            logger.debug("Updated R1 signal", signal=r1_signal)

        if janus_confidence is not None:
            self._last_janus_confidence = janus_confidence
            logger.debug("Updated Janus confidence", confidence=janus_confidence)

    async def analyze(self, context: dict[str, Any]) -> AgentReport:
        """
        Main entry point for execution analysis.

        Args:
            context: Contains strategy_proposal, market data, etc.

        Returns:
            AgentReport with execution decision
        """
        report = await self.get_execution_decision(context)
        symbol = context.get("symbol", "UNKNOWN")

        return AgentReport(
            agent_role=self.role,
            symbol=symbol,
            summary=f"RL execution decision: {report.action_type} "
                    f"(confidence: {report.execution_confidence:.2f})",
            confidence=report.execution_confidence,
            metadata={"execution_report": report.model_dump()},
        )

    async def get_execution_decision(
        self, context: dict[str, Any]
    ) -> FinRLExecutionReport:
        """
        Get execution decision from FinRL agent.

        Args:
            context: Contains market data, strategy, signals

        Returns:
            FinRLExecutionReport with action and confidence
        """
        symbol = context.get("symbol", "UNKNOWN")

        logger.info("Getting FinRL execution decision", symbol=symbol)

        try:
            # Build state vector
            state = self._build_state_vector(context)

            # Check if FinRL service is enabled
            if settings.finrl_enabled:
                report = await self._get_finrl_decision(symbol, state, context)
            else:
                # Fallback to rule-based execution
                report = await self._rule_based_execution(symbol, state, context)

            logger.info(
                "Execution decision complete",
                symbol=symbol,
                action=report.action_type,
                confidence=report.execution_confidence,
            )

            return report

        except Exception as e:
            logger.error("Execution decision failed", symbol=symbol, error=str(e))
            return FinRLExecutionReport(
                symbol=symbol,
                summary=f"Execution failed: {str(e)}",
                confidence=0.1,
                action_type="hold",
                execution_confidence=0.1,
            )

    def _build_state_vector(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Build state vector for RL agent.

        Combines market data with strategic signals from R1/Janus.

        Args:
            context: Contains market data and signals

        Returns:
            State dictionary for RL agent
        """
        # Extract market data
        current_price = context.get("current_price", 0.0)
        bid = context.get("bid", current_price)
        ask = context.get("ask", current_price)
        volume = context.get("volume", 0)

        # Technical indicators
        tech_indicators = context.get("technical_indicators", {})
        rsi = tech_indicators.get("rsi", 50.0)
        macd = tech_indicators.get("macd", 0.0)

        # Strategy signals
        strategy_proposal: Optional[StrategyProposal] = context.get("strategy_proposal")
        strategy_direction = 0.0
        if strategy_proposal:
            # Handle direction as either enum or string
            direction = strategy_proposal.direction
            direction_str = (
                direction.value if hasattr(direction, "value") else str(direction)
            )
            if direction_str == "long":
                strategy_direction = 1.0
            elif direction_str == "short":
                strategy_direction = -1.0

        # Use last known R1/Janus signals (asynchronous updates)
        r1_signal = context.get("r1_signal", self._last_r1_signal)
        janus_confidence = context.get("janus_confidence", self._last_janus_confidence)

        state = {
            # Market microstructure
            "price": current_price,
            "bid": bid,
            "ask": ask,
            "spread": ask - bid if ask and bid else 0.0,
            "volume": volume,
            # Technical
            "rsi": rsi,
            "macd": macd,
            "rsi_normalized": (rsi - 50) / 50,  # -1 to 1
            # Strategic signals (from slow/medium loops)
            "r1_sentiment": r1_signal,
            "janus_pattern_confidence": janus_confidence,
            "strategy_direction": strategy_direction,
            # Combined signal
            "combined_signal": (
                r1_signal * 0.3 +
                janus_confidence * strategy_direction * 0.3 +
                strategy_direction * 0.4
            ),
        }

        return state

    async def _get_finrl_decision(
        self,
        symbol: str,
        state: dict[str, Any],
        context: dict[str, Any],
    ) -> FinRLExecutionReport:
        """
        Get decision from FinRL REST API.

        Args:
            symbol: Stock symbol
            state: State vector
            context: Full context

        Returns:
            FinRLExecutionReport from RL agent
        """
        session = await self._get_session()

        payload = {
            "symbol": symbol,
            "state": state,
            "agent_type": settings.finrl_agent_type,
        }

        try:
            endpoint = f"{settings.finrl_endpoint}/predict"
            async with session.post(
                endpoint,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=5),  # Fast timeout
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return self._parse_finrl_response(symbol, result, state)
                else:
                    error = await response.text()
                    logger.warning(
                        "FinRL API error",
                        status=response.status,
                        error=error,
                    )
                    return await self._rule_based_execution(symbol, state, context)

        except aiohttp.ClientError as e:
            logger.warning("FinRL connection failed", error=str(e))
            return await self._rule_based_execution(symbol, state, context)

    def _parse_finrl_response(
        self,
        symbol: str,
        result: dict,
        state: dict,
    ) -> FinRLExecutionReport:
        """Parse FinRL API response into a report."""
        action = result.get("action", 0)  # -1: sell, 0: hold, 1: buy
        confidence = result.get("confidence", 0.5)
        amount = abs(result.get("amount", 0.0))

        # Map action to string
        if action > 0:
            action_type = "buy"
        elif action < 0:
            action_type = "sell"
        else:
            action_type = "hold"

        return FinRLExecutionReport(
            symbol=symbol,
            summary=f"FinRL {settings.finrl_agent_type.upper()} decision: {action_type}",
            confidence=confidence,
            action_type=action_type,
            action_amount=amount,
            execution_confidence=confidence,
            state_embedding=state,
            r1_sentiment_signal=state.get("r1_sentiment", 0.0),
            janus_pattern_confidence=state.get("janus_pattern_confidence", 0.0),
            execution_timing=result.get("timing", "immediate"),
            slippage_estimate=result.get("slippage_estimate", 0.0),
            rl_policy_output=result.get("policy_output", {}),
        )

    async def _rule_based_execution(
        self,
        symbol: str,
        state: dict[str, Any],
        context: dict[str, Any],
    ) -> FinRLExecutionReport:
        """
        Rule-based execution fallback when FinRL is unavailable.

        Uses combined signals from R1/Janus and strategy direction.

        Args:
            symbol: Stock symbol
            state: State vector
            context: Full context

        Returns:
            FinRLExecutionReport from rule-based logic
        """
        logger.info("Using rule-based execution fallback", symbol=symbol)

        combined_signal = state.get("combined_signal", 0.0)
        strategy_direction = state.get("strategy_direction", 0.0)

        # Decision thresholds
        buy_threshold = 0.3
        sell_threshold = -0.3

        if combined_signal > buy_threshold:
            action_type = "buy"
            confidence = min(1.0, (combined_signal - buy_threshold) / 0.7 + 0.5)
        elif combined_signal < sell_threshold:
            action_type = "sell"
            confidence = min(1.0, (sell_threshold - combined_signal) / 0.7 + 0.5)
        else:
            action_type = "hold"
            confidence = 0.5

        # Adjust confidence based on R1/Janus signals
        if state.get("r1_sentiment", 0) * strategy_direction > 0:
            confidence *= 1.1  # Boost if R1 agrees with strategy
        if state.get("janus_pattern_confidence", 0) > 0.7:
            confidence *= 1.05  # Boost if Janus has high confidence

        confidence = min(1.0, confidence)

        # Estimate slippage from spread
        spread = state.get("spread", 0.0)
        price = state.get("price", 1.0)
        slippage_estimate = (spread / price * 100) if price > 0 else 0.1

        return FinRLExecutionReport(
            symbol=symbol,
            summary=f"Rule-based execution: {action_type}",
            confidence=confidence,
            action_type=action_type,
            action_amount=context.get("position_size", 0.0),
            execution_confidence=confidence,
            state_embedding=state,
            r1_sentiment_signal=state.get("r1_sentiment", 0.0),
            janus_pattern_confidence=state.get("janus_pattern_confidence", 0.0),
            execution_timing="immediate",
            slippage_estimate=slippage_estimate,
        )

    async def create_execution_plan(
        self, context: dict[str, Any]
    ) -> ExecutionPlan:
        """
        Create execution plan based on RL decision.

        Args:
            context: Contains strategy_proposal, market data, etc.

        Returns:
            ExecutionPlan with order specifications
        """
        symbol = context.get("symbol", "UNKNOWN")
        strategy_proposal: Optional[StrategyProposal] = context.get("strategy_proposal")

        # Get RL decision
        decision = await self.get_execution_decision(context)

        if decision.action_type == "hold" or not strategy_proposal:
            return ExecutionPlan(
                agent_role=self.role,
                orders=[],
                execution_strategy="No action - holding position",
                notes="RL agent recommends holding",
            )

        # Map RL decision to order
        current_price = context.get("current_price", 0.0)
        portfolio_value = context.get("portfolio_value", 100000.0)
        position_value = portfolio_value * strategy_proposal.position_size_pct

        if current_price > 0:
            quantity = int(position_value / current_price)
            quantity = max(1, quantity)
        else:
            quantity = 100

        side = OrderSide.BUY if decision.action_type == "buy" else OrderSide.SELL

        # Use limit order for better execution
        limit_price = current_price * (1.001 if side == OrderSide.BUY else 0.999)

        order = Order(
            symbol=symbol,
            side=side.value,
            order_type=OrderType.LIMIT.value,
            quantity=float(quantity),
            limit_price=limit_price,
            time_in_force="DAY",
        )

        return ExecutionPlan(
            agent_role=self.role,
            orders=[order],
            execution_strategy=f"RL-optimized {decision.action_type}",
            notes=f"FinRL confidence: {decision.execution_confidence:.2f}, "
                  f"R1 signal: {decision.r1_sentiment_signal:.2f}, "
                  f"Janus confidence: {decision.janus_pattern_confidence:.2f}",
        )
