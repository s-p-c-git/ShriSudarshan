"""Execution Team - Equity Trader."""

import json
from typing import Any, Dict

from ..base import BaseAgent
from ...config.prompts import EQUITY_TRADER_PROMPT
from ...data.schemas import (
    AgentRole,
    ExecutionPlan,
    StrategyProposal,
    Order,
    OrderType,
    OrderSide,
)
from ...data.providers import MarketDataProvider
from ...utils import get_logger

logger = get_logger(__name__)


class EquityTrader(BaseAgent):
    """
    Equity Trader agent.
    
    Focuses on optimal execution for stock trades, determining the best
    order types, timing, and sizing to minimize slippage and market impact.
    """
    
    def __init__(self):
        super().__init__(
            role=AgentRole.EQUITY_TRADER,
            system_prompt=EQUITY_TRADER_PROMPT,
            temperature=0.5,
        )
        self.market_data_provider = MarketDataProvider()
    
    async def create_execution_plan(self, context: Dict[str, Any]) -> ExecutionPlan:
        """
        Create detailed execution plan for equity trades.
        
        Args:
            context: Contains strategy_proposal, symbol, etc.
            
        Returns:
            ExecutionPlan with order specifications
        """
        symbol = context.get("symbol", "UNKNOWN")
        strategy_proposal: StrategyProposal = context.get("strategy_proposal")
        
        if not strategy_proposal:
            raise ValueError("No strategy proposal provided")
        
        # Use provided provider or default
        data_provider = context.get("market_data_provider", self.market_data_provider)
        
        logger.info("Creating execution plan", symbol=symbol, strategy=strategy_proposal.strategy_type.value)
        
        try:
            # Get current market data
            current_price = data_provider.get_current_price(symbol)
            quote = data_provider.get_quote(symbol)
            
            # Calculate position size in shares
            # Assuming a $100,000 portfolio for now
            portfolio_value = context.get("portfolio_value", 100000.0)
            position_value = portfolio_value * strategy_proposal.position_size_pct
            
            if current_price and current_price > 0:
                quantity = int(position_value / current_price)
                quantity = max(1, quantity)  # At least 1 share
            else:
                quantity = 100  # Default
            
            # Determine order side
            if strategy_proposal.strategy_type.value in ["LONG_EQUITY", "COVERED_CALL", "PROTECTIVE_PUT"]:
                side = OrderSide.BUY
            elif strategy_proposal.strategy_type.value == "SHORT_EQUITY":
                side = OrderSide.SELL
            else:
                side = OrderSide.BUY  # Default to buy
            
            # Get bid/ask spread for slippage estimation
            bid = quote.get("bid", current_price) if quote else current_price
            ask = quote.get("ask", current_price) if quote else current_price
            spread = abs(ask - bid) if bid and ask else 0
            slippage_estimate = (spread / current_price * 100) if current_price else 0.1
            
            # Construct input for LLM
            input_text = f"""
Create an execution plan for {symbol} based on the approved strategy.

STRATEGY:
- Type: {strategy_proposal.strategy_type.value}
- Direction: {strategy_proposal.direction.value}
- Position Size: {strategy_proposal.position_size_pct * 100:.1f}% of portfolio
- Shares to Trade: {quantity}
- Side: {side.value}

MARKET DATA:
- Current Price: ${current_price or 'N/A'}
- Bid: ${bid or 'N/A'}
- Ask: ${ask or 'N/A'}
- Spread: ${spread:.4f} ({slippage_estimate:.3f}%)
- Volume: {quote.get('volume', 'N/A') if quote else 'N/A'}

EXECUTION REQUIREMENTS:
- Minimize slippage and market impact
- Consider liquidity and volume patterns
- Use appropriate order types
- Plan for contingencies

Provide your execution plan in JSON format:
{{
    "order_type": "MARKET" or "LIMIT" or "STOP" or "STOP_LIMIT",
    "limit_price": <price for limit orders, null otherwise>,
    "execution_timing": "description of timing strategy",
    "slippage_tolerance": <percentage>,
    "contingency_plans": ["plan1", "plan2"],
    "rationale": "brief explanation"
}}
"""
            
            # Generate execution plan
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
                
                order_type_str = parsed.get("order_type", "LIMIT")
                limit_price = parsed.get("limit_price")
                execution_timing = parsed.get("execution_timing", "Immediate execution at market open")
                slippage_tolerance = float(parsed.get("slippage_tolerance", 0.5))
                contingency_plans = parsed.get("contingency_plans", [])
                rationale = parsed.get("rationale", "Execution plan based on strategy")
                
                # Map order type
                try:
                    order_type = OrderType(order_type_str)
                except ValueError:
                    order_type = OrderType.LIMIT  # Default to limit order for safety
                
                # Set limit price if not provided
                if order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT]:
                    if not limit_price:
                        if side == OrderSide.BUY:
                            limit_price = ask if ask else current_price * 1.01
                        else:
                            limit_price = bid if bid else current_price * 0.99
                
            except (json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
                logger.warning("Failed to parse response, using defaults", error=str(e))
                
                # Conservative defaults
                order_type = OrderType.LIMIT
                if side == OrderSide.BUY:
                    limit_price = ask if ask else current_price * 1.01
                else:
                    limit_price = bid if bid else current_price * 0.99
                execution_timing = "Immediate execution"
                slippage_tolerance = 0.5
                contingency_plans = ["Cancel and reassess if not filled within 5 minutes"]
                rationale = response[:200]
            
            # Create order
            order = Order(
                symbol=symbol,
                order_type=order_type,
                side=side,
                quantity=quantity,
                limit_price=limit_price,
                stop_price=None,
                time_in_force="DAY",
            )
            
            # Estimate costs
            commission = 0.0  # Assuming commission-free trading
            estimated_slippage = position_value * (slippage_tolerance / 100)
            estimated_cost = commission + estimated_slippage
            
            plan = ExecutionPlan(
                symbol=symbol,
                strategy_type=strategy_proposal.strategy_type,
                orders=[order],
                execution_timing=execution_timing,
                slippage_tolerance=slippage_tolerance,
                contingency_plans=contingency_plans,
                estimated_cost=estimated_cost,
            )
            
            logger.info(
                "Execution plan created",
                symbol=symbol,
                order_type=order_type.value,
                quantity=quantity,
                side=side.value,
            )
            
            return plan
            
        except Exception as e:
            logger.error("Execution planning failed", symbol=symbol, error=str(e))
            
            # Return minimal plan
            return ExecutionPlan(
                symbol=symbol,
                strategy_type=strategy_proposal.strategy_type,
                orders=[],
                execution_timing="Manual execution required",
                slippage_tolerance=1.0,
                contingency_plans=["Manual review required"],
                estimated_cost=0.0,
            )
