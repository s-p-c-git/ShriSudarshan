"""Execution Team - FnO Trader."""

import json
from typing import Any

from ...config.prompts import FNO_TRADER_PROMPT
from ...data.providers import MarketDataProvider
from ...data.schemas import (
    AgentRole,
    ExecutionPlan,
    Order,
    OrderSide,
    OrderType,
    StrategyProposal,
    StrategyType,
)
from ...utils import get_logger
from ..base import BaseAgent


logger = get_logger(__name__)


class FnOTrader(BaseAgent):
    """
    FnO (Futures & Options) Trader agent.

    Executes complex multi-leg options and futures strategies.
    """

    def __init__(self):
        super().__init__(
            role=AgentRole.FNO_TRADER,
            system_prompt=FNO_TRADER_PROMPT,
            temperature=0.5,
        )
        self.market_data_provider = MarketDataProvider()

    def _create_option_legs(
        self,
        symbol: str,
        strategy_type: StrategyType,
        current_price: float,
        portfolio_value: float,
        position_size_pct: float,
    ) -> list[Order]:
        """
        Create option leg orders based on strategy type.

        Args:
            symbol: Stock symbol
            strategy_type: Type of options strategy
            current_price: Current stock price
            portfolio_value: Total portfolio value
            position_size_pct: Position size as percentage

        Returns:
            List of Order objects for each leg
        """
        orders = []
        position_value = portfolio_value * position_size_pct

        # Note: In production, would use real options data for strikes and expirations
        # For now, using simplified logic

        if strategy_type == StrategyType.COVERED_CALL:
            # Buy 100 shares + Sell 1 ATM call
            shares = int(position_value / current_price)
            shares = max(100, (shares // 100) * 100)  # Round to lot size

            orders.append(
                Order(
                    symbol=symbol,
                    order_type=OrderType.LIMIT,
                    side=OrderSide.BUY,
                    quantity=shares,
                    limit_price=current_price * 1.01,
                )
            )

            # Sell call (simplified - would use actual options symbol)
            strike = current_price * 1.05
            orders.append(
                Order(
                    symbol=f"{symbol}_CALL_{strike:.0f}",
                    order_type=OrderType.LIMIT,
                    side=OrderSide.SELL,
                    quantity=shares // 100,
                    limit_price=current_price * 0.03,  # Simplified premium
                )
            )

        elif strategy_type == StrategyType.PROTECTIVE_PUT:
            # Buy 100 shares + Buy 1 OTM put
            shares = int(position_value / current_price)
            shares = max(100, (shares // 100) * 100)

            orders.append(
                Order(
                    symbol=symbol,
                    order_type=OrderType.LIMIT,
                    side=OrderSide.BUY,
                    quantity=shares,
                    limit_price=current_price * 1.01,
                )
            )

            # Buy put
            strike = current_price * 0.95
            orders.append(
                Order(
                    symbol=f"{symbol}_PUT_{strike:.0f}",
                    order_type=OrderType.LIMIT,
                    side=OrderSide.BUY,
                    quantity=shares // 100,
                    limit_price=current_price * 0.02,
                )
            )

        elif strategy_type == StrategyType.BULL_CALL_SPREAD:
            # Buy ATM call, Sell OTM call
            contracts = max(1, int(position_value / (current_price * 100) / 2))

            strike_buy = current_price
            strike_sell = current_price * 1.05

            orders.append(
                Order(
                    symbol=f"{symbol}_CALL_{strike_buy:.0f}",
                    order_type=OrderType.LIMIT,
                    side=OrderSide.BUY,
                    quantity=contracts,
                    limit_price=current_price * 0.05,
                )
            )

            orders.append(
                Order(
                    symbol=f"{symbol}_CALL_{strike_sell:.0f}",
                    order_type=OrderType.LIMIT,
                    side=OrderSide.SELL,
                    quantity=contracts,
                    limit_price=current_price * 0.03,
                )
            )

        elif strategy_type == StrategyType.BEAR_PUT_SPREAD:
            # Buy ATM put, Sell OTM put
            contracts = max(1, int(position_value / (current_price * 100) / 2))

            strike_buy = current_price
            strike_sell = current_price * 0.95

            orders.append(
                Order(
                    symbol=f"{symbol}_PUT_{strike_buy:.0f}",
                    order_type=OrderType.LIMIT,
                    side=OrderSide.BUY,
                    quantity=contracts,
                    limit_price=current_price * 0.05,
                )
            )

            orders.append(
                Order(
                    symbol=f"{symbol}_PUT_{strike_sell:.0f}",
                    order_type=OrderType.LIMIT,
                    side=OrderSide.SELL,
                    quantity=contracts,
                    limit_price=current_price * 0.03,
                )
            )

        elif strategy_type == StrategyType.STRADDLE:
            # Buy ATM call + Buy ATM put
            contracts = max(1, int(position_value / (current_price * 100) / 2))
            strike = current_price

            orders.append(
                Order(
                    symbol=f"{symbol}_CALL_{strike:.0f}",
                    order_type=OrderType.LIMIT,
                    side=OrderSide.BUY,
                    quantity=contracts,
                    limit_price=current_price * 0.05,
                )
            )

            orders.append(
                Order(
                    symbol=f"{symbol}_PUT_{strike:.0f}",
                    order_type=OrderType.LIMIT,
                    side=OrderSide.BUY,
                    quantity=contracts,
                    limit_price=current_price * 0.05,
                )
            )

        elif strategy_type == StrategyType.STRANGLE:
            # Buy OTM call + Buy OTM put
            contracts = max(1, int(position_value / (current_price * 100) / 2))

            strike_call = current_price * 1.05
            strike_put = current_price * 0.95

            orders.append(
                Order(
                    symbol=f"{symbol}_CALL_{strike_call:.0f}",
                    order_type=OrderType.LIMIT,
                    side=OrderSide.BUY,
                    quantity=contracts,
                    limit_price=current_price * 0.03,
                )
            )

            orders.append(
                Order(
                    symbol=f"{symbol}_PUT_{strike_put:.0f}",
                    order_type=OrderType.LIMIT,
                    side=OrderSide.BUY,
                    quantity=contracts,
                    limit_price=current_price * 0.03,
                )
            )

        elif strategy_type == StrategyType.IRON_CONDOR:
            # Sell call spread + Sell put spread (4 legs)
            # Profit from low volatility / range-bound movement
            contracts = max(1, int(position_value / (current_price * 100) / 4))

            # Call spread (sell ATM, buy OTM call)
            strike_sell_call = current_price * 1.025
            strike_buy_call = current_price * 1.05

            orders.append(
                Order(
                    symbol=f"{symbol}_CALL_{strike_sell_call:.0f}",
                    order_type=OrderType.LIMIT,
                    side=OrderSide.SELL,
                    quantity=contracts,
                    limit_price=current_price * 0.04,
                )
            )

            orders.append(
                Order(
                    symbol=f"{symbol}_CALL_{strike_buy_call:.0f}",
                    order_type=OrderType.LIMIT,
                    side=OrderSide.BUY,
                    quantity=contracts,
                    limit_price=current_price * 0.02,
                )
            )

            # Put spread (sell ATM, buy OTM put)
            strike_sell_put = current_price * 0.975
            strike_buy_put = current_price * 0.95

            orders.append(
                Order(
                    symbol=f"{symbol}_PUT_{strike_sell_put:.0f}",
                    order_type=OrderType.LIMIT,
                    side=OrderSide.SELL,
                    quantity=contracts,
                    limit_price=current_price * 0.04,
                )
            )

            orders.append(
                Order(
                    symbol=f"{symbol}_PUT_{strike_buy_put:.0f}",
                    order_type=OrderType.LIMIT,
                    side=OrderSide.BUY,
                    quantity=contracts,
                    limit_price=current_price * 0.02,
                )
            )

        elif strategy_type == StrategyType.CALENDAR_SPREAD:
            # Buy far-dated option + Sell near-dated option (same strike)
            contracts = max(1, int(position_value / (current_price * 100) / 2))
            strike = current_price

            # Sell near-dated call (30 days out - simplified)
            orders.append(
                Order(
                    symbol=f"{symbol}_CALL_{strike:.0f}_30D",
                    order_type=OrderType.LIMIT,
                    side=OrderSide.SELL,
                    quantity=contracts,
                    limit_price=current_price * 0.03,
                )
            )

            # Buy far-dated call (60 days out - simplified)
            orders.append(
                Order(
                    symbol=f"{symbol}_CALL_{strike:.0f}_60D",
                    order_type=OrderType.LIMIT,
                    side=OrderSide.BUY,
                    quantity=contracts,
                    limit_price=current_price * 0.05,
                )
            )

        return orders

    async def create_execution_plan(self, context: dict[str, Any]) -> ExecutionPlan:
        """
        Create detailed execution plan for options/futures trades.

        Args:
            context: Contains strategy_proposal, symbol, etc.

        Returns:
            ExecutionPlan with multi-leg order specifications
        """
        symbol = context.get("symbol", "UNKNOWN")
        strategy_proposal: StrategyProposal = context.get("strategy_proposal")

        if not strategy_proposal:
            raise ValueError("No strategy proposal provided")

        # Use provided provider or default
        data_provider = context.get("market_data_provider", self.market_data_provider)

        logger.info(
            "Creating FnO execution plan",
            symbol=symbol,
            strategy=strategy_proposal.strategy_type.value,
        )

        try:
            # Get current market data
            current_price = data_provider.get_current_price(symbol)

            if not current_price:
                raise ValueError("Unable to fetch current price")

            # Get portfolio value
            portfolio_value = context.get("portfolio_value", 100000.0)

            # Create option legs based on strategy type
            if strategy_proposal.strategy_type in [
                StrategyType.COVERED_CALL,
                StrategyType.PROTECTIVE_PUT,
                StrategyType.BULL_CALL_SPREAD,
                StrategyType.BEAR_PUT_SPREAD,
                StrategyType.IRON_CONDOR,
                StrategyType.STRADDLE,
                StrategyType.STRANGLE,
                StrategyType.CALENDAR_SPREAD,
            ]:
                orders = self._create_option_legs(
                    symbol,
                    strategy_proposal.strategy_type,
                    current_price,
                    portfolio_value,
                    strategy_proposal.position_size_pct,
                )
            else:
                # For non-options strategies, return empty orders
                orders = []

            # Construct input for LLM to refine execution
            input_text = f"""
Create an execution plan for the {strategy_proposal.strategy_type.value} strategy on {symbol}.

STRATEGY:
- Type: {strategy_proposal.strategy_type.value}
- Direction: {strategy_proposal.direction.value}
- Number of Legs: {len(orders)}

MARKET DATA:
- Current Price: ${current_price:.2f}

EXECUTION CONSIDERATIONS:
- Multi-leg order execution sequence
- Liquidity assessment for each leg
- Greeks management during execution
- Spread pricing and fills

Provide execution guidance in JSON format:
{{
    "execution_sequence": "description of leg-by-leg execution order",
    "timing_strategy": "when and how to execute",
    "risk_during_execution": "risks while legs are being filled",
    "monitoring_requirements": ["requirement1", "requirement2"],
    "contingency_plans": ["plan1", "plan2"]
}}
"""

            # Generate execution guidance
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

                execution_timing = parsed.get(
                    "execution_sequence", "Execute all legs simultaneously"
                )
                contingency_plans = parsed.get("contingency_plans", [])

            except (json.JSONDecodeError, KeyError, IndexError) as e:
                logger.warning("Failed to parse response, using defaults", error=str(e))
                execution_timing = "Execute legs in sequence, starting with long positions"
                contingency_plans = ["Cancel remaining legs if first leg fails"]

            # Estimate costs
            position_value = portfolio_value * strategy_proposal.position_size_pct
            estimated_slippage = position_value * 0.01  # 1% slippage for options
            estimated_cost = estimated_slippage

            plan = ExecutionPlan(
                symbol=symbol,
                strategy_type=strategy_proposal.strategy_type,
                orders=orders,
                execution_timing=execution_timing,
                slippage_tolerance=1.0,
                contingency_plans=contingency_plans,
                estimated_cost=estimated_cost,
            )

            logger.info(
                "FnO execution plan created",
                symbol=symbol,
                strategy=strategy_proposal.strategy_type.value,
                legs=len(orders),
            )

            return plan

        except Exception as e:
            logger.error("FnO execution planning failed", symbol=symbol, error=str(e))

            # Return minimal plan
            return ExecutionPlan(
                symbol=symbol,
                strategy_type=strategy_proposal.strategy_type,
                orders=[],
                execution_timing="Manual execution required",
                slippage_tolerance=2.0,
                contingency_plans=["Manual review required"],
                estimated_cost=0.0,
            )
