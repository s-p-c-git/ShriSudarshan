"""Strategy & Research Team - Derivatives Strategist."""

import json
from typing import Any

from ...config.prompts import DERIVATIVES_STRATEGIST_PROMPT
from ...data.providers import MarketDataProvider
from ...data.schemas import (
    AgentRole,
    Sentiment,
    StrategyProposal,
    StrategyType,
)
from ...utils import get_logger
from ..base import CriticalAgent


logger = get_logger(__name__)


class DerivativesStrategist(CriticalAgent):
    """
    Derivatives Strategist (FnO Specialist) agent.

    Analyzes options data and proposes specific FnO strategies based on
    the debate outcome.
    """

    def __init__(self):
        super().__init__(
            role=AgentRole.DERIVATIVES_STRATEGIST,
            system_prompt=DERIVATIVES_STRATEGIST_PROMPT,
            temperature=0.6,
        )
        self.market_data_provider = MarketDataProvider()

    async def formulate_strategy(self, context: dict[str, Any]) -> StrategyProposal:
        """
        Formulate trading strategy based on debate outcome.

        Args:
            context: Contains symbol, debate_arguments, analyst_reports

        Returns:
            StrategyProposal with detailed strategy
        """
        symbol = context.get("symbol", "UNKNOWN")
        debate_arguments = context.get("debate_arguments", [])
        analyst_reports = context.get("analyst_reports", {})

        # Use provided provider or default
        data_provider = context.get("market_data_provider", self.market_data_provider)

        logger.info("Formulating strategy", symbol=symbol)

        try:
            # Analyze debate outcome
            bullish_args = [arg for arg in debate_arguments if arg.position == Sentiment.BULLISH]
            bearish_args = [arg for arg in debate_arguments if arg.position == Sentiment.BEARISH]

            # Determine overall sentiment from debate
            bullish_strength = len(bullish_args)
            bearish_strength = len(bearish_args)

            if bullish_strength > bearish_strength:
                overall_direction = Sentiment.BULLISH
            elif bearish_strength > bullish_strength:
                overall_direction = Sentiment.BEARISH
            else:
                overall_direction = Sentiment.NEUTRAL

            # Get current price and options data
            current_price = data_provider.get_current_price(symbol)

            try:
                options_data = data_provider.get_options_chain(symbol)
                has_options = len(options_data.get("calls", [])) > 0
            except Exception:
                has_options = False
                options_data = {}

            # Prepare debate summary
            debate_summary = f"""
Debate Outcome:
- Bullish Arguments: {bullish_strength}
- Bearish Arguments: {bearish_strength}
- Direction: {overall_direction.value}

Latest Bullish Points:
{bullish_args[-1].argument[:300] if bullish_args else "None"}

Latest Bearish Points:
{bearish_args[-1].argument[:300] if bearish_args else "None"}
"""

            # Get technical levels for strike selection
            technical = analyst_reports.get("technical")
            support_levels = technical.support_levels if technical else []
            resistance_levels = technical.resistance_levels if technical else []

            # Construct input for LLM
            input_text = f"""
Formulate a trading strategy for {symbol} based on the debate outcome and analysis.

DEBATE SUMMARY:
{debate_summary}

MARKET DATA:
- Current Price: ${current_price or "N/A"}
- Options Available: {has_options}
- Support Levels: {", ".join([f"${x:.2f}" for x in support_levels])}
- Resistance Levels: {", ".join([f"${x:.2f}" for x in resistance_levels])}

SENTIMENT:
- Overall Direction: {overall_direction.value}

Based on the analysis, formulate a strategy that:
1. Aligns with the consensus view from the debate
2. Has clear entry and exit conditions
3. Manages risk appropriately
4. Specifies position sizing

Choose from these strategy types:
- LONG_EQUITY: Buy stock (bullish, simple)
- SHORT_EQUITY: Short stock (bearish, simple)
- COVERED_CALL: Own stock + sell calls (neutral to slightly bullish)
- PROTECTIVE_PUT: Own stock + buy puts (bullish with protection)
- BULL_CALL_SPREAD: Buy call + sell higher call (moderately bullish)
- BEAR_PUT_SPREAD: Buy put + sell lower put (moderately bearish)
- IRON_CONDOR: Sell both spreads (neutral, range-bound)
- STRADDLE: Buy call + put (expecting big move, uncertain direction)
- STRANGLE: Buy OTM call + OTM put (expecting big move, cheaper than straddle)
- CALENDAR_SPREAD: Buy far-dated + sell near-dated options (profit from time decay)

Provide your strategy in JSON format:
{{
    "strategy_type": "one of the types above",
    "rationale": "why this strategy fits the analysis",
    "entry_conditions": ["condition1", "condition2"],
    "exit_conditions": ["condition1", "condition2"],
    "position_size_pct": <0.01 to 0.05>,
    "expected_return": <percentage>,
    "max_loss": <percentage>,
    "time_horizon_days": <number>,
    "confidence_score": <0.0 to 1.0>
}}
"""

            # Generate strategy
            response = await self._generate_response(input_text)

            # Parse JSON response
            try:
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0].strip()
                else:
                    json_str = response.strip()

                parsed = json.loads(json_str)

                strategy_type_str = parsed.get("strategy_type", "LONG_EQUITY")
                rationale = parsed.get("rationale", "Strategy based on analysis")
                entry_conditions = parsed.get(
                    "entry_conditions", [f"Current price: ${current_price}"]
                )
                exit_conditions = parsed.get("exit_conditions", ["Target reached or stop hit"])
                position_size_pct = float(parsed.get("position_size_pct", 0.02))
                expected_return = float(parsed.get("expected_return", 10.0))
                max_loss = float(parsed.get("max_loss", -5.0))
                time_horizon_days = int(parsed.get("time_horizon_days", 30))
                confidence_score = float(parsed.get("confidence_score", 0.6))

                # Map strategy type string to enum
                try:
                    strategy_type = StrategyType(strategy_type_str)
                except ValueError:
                    # Default based on direction
                    if overall_direction == Sentiment.BULLISH:
                        strategy_type = StrategyType.LONG_EQUITY
                    elif overall_direction == Sentiment.BEARISH:
                        strategy_type = StrategyType.SHORT_EQUITY
                    else:
                        strategy_type = StrategyType.IRON_CONDOR

                # Clamp values
                position_size_pct = max(0.001, min(0.05, position_size_pct))
                confidence_score = max(0.0, min(1.0, confidence_score))

            except (json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
                logger.warning("Failed to parse response, using defaults", error=str(e))

                # Default strategy based on direction
                if overall_direction == Sentiment.BULLISH:
                    strategy_type = StrategyType.LONG_EQUITY
                elif overall_direction == Sentiment.BEARISH:
                    strategy_type = StrategyType.SHORT_EQUITY
                else:
                    strategy_type = StrategyType.IRON_CONDOR

                rationale = response[:200]
                entry_conditions = ["Market conditions favorable"]
                exit_conditions = ["Target or stop reached"]
                position_size_pct = 0.02
                expected_return = 10.0
                max_loss = -5.0
                time_horizon_days = 30
                confidence_score = 0.6

            proposal = StrategyProposal(
                symbol=symbol,
                strategy_type=strategy_type,
                direction=overall_direction,
                rationale=rationale,
                entry_conditions=entry_conditions,
                exit_conditions=exit_conditions,
                position_size_pct=position_size_pct,
                expected_return=expected_return,
                max_loss=max_loss,
                time_horizon_days=time_horizon_days,
                confidence_score=confidence_score,
                debate_summary=debate_summary,
            )

            logger.info(
                "Strategy formulated",
                symbol=symbol,
                strategy=strategy_type.value,
                direction=overall_direction.value,
                confidence=confidence_score,
            )

            return proposal

        except Exception as e:
            logger.error("Strategy formulation failed", symbol=symbol, error=str(e))

            # Return conservative default strategy
            return StrategyProposal(
                symbol=symbol,
                strategy_type=StrategyType.LONG_EQUITY,
                direction=Sentiment.NEUTRAL,
                rationale=f"Error in strategy formulation: {str(e)}",
                entry_conditions=["Manual review required"],
                exit_conditions=["Manual review required"],
                position_size_pct=0.01,
                expected_return=0.0,
                max_loss=-5.0,
                time_horizon_days=30,
                confidence_score=0.1,
                debate_summary="Error occurred during strategy formulation",
            )
