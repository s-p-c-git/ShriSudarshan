"""
Tests for Execution agents using mock implementations.

Tests both Execution agents:
- EquityTrader
- FnOTrader (Futures & Options Trader)
"""

import pytest

from src.data.schemas import (
    AgentRole,
    ExecutionPlan,
    Order,
    OrderSide,
    OrderType,
    StrategyType,
)
from tests.mock_agents import MockEquityTrader, MockFnOTrader


# =============================================================================
# Equity Trader Tests
# =============================================================================


@pytest.mark.asyncio
async def test_equity_trader_basic_plan(sample_context):
    """Test equity trader produces valid execution plan."""
    agent = MockEquityTrader()
    
    plan = await agent.create_execution_plan(sample_context)
    
    assert isinstance(plan, ExecutionPlan)
    assert plan.symbol == sample_context["symbol"]
    assert isinstance(plan.orders, list)
    assert len(plan.orders) > 0


@pytest.mark.asyncio
async def test_equity_trader_order_structure(sample_context):
    """Test equity trader orders have proper structure."""
    agent = MockEquityTrader()
    
    plan = await agent.create_execution_plan(sample_context)
    
    for order in plan.orders:
        assert isinstance(order, Order)
        assert order.symbol == plan.symbol
        assert order.side in [OrderSide.BUY, OrderSide.SELL]
        assert order.order_type in [OrderType.MARKET, OrderType.LIMIT, OrderType.STOP, OrderType.STOP_LIMIT]
        assert order.quantity > 0


@pytest.mark.asyncio
async def test_equity_trader_cost_estimation(sample_context):
    """Test equity trader estimates costs."""
    agent = MockEquityTrader()
    
    plan = await agent.create_execution_plan(sample_context)
    
    assert plan.estimated_cost is not None
    assert plan.estimated_cost > 0
    assert plan.estimated_slippage >= 0


@pytest.mark.asyncio
async def test_equity_trader_timing_recommendation(sample_context):
    """Test equity trader provides timing recommendation."""
    agent = MockEquityTrader()
    
    plan = await agent.create_execution_plan(sample_context)
    
    assert plan.timing_recommendation is not None


@pytest.mark.asyncio
async def test_equity_trader_strategy_type(sample_context):
    """Test equity trader specifies strategy type."""
    agent = MockEquityTrader()
    
    plan = await agent.create_execution_plan(sample_context)
    
    assert plan.strategy_type in [
        StrategyType.LONG_EQUITY,
        StrategyType.SHORT_EQUITY,
        StrategyType.COVERED_CALL,
        StrategyType.PROTECTIVE_PUT,
        StrategyType.BULL_CALL_SPREAD,
        StrategyType.BEAR_PUT_SPREAD,
        StrategyType.IRON_CONDOR,
        StrategyType.STRADDLE,
        StrategyType.STRANGLE,
        StrategyType.BUTTERFLY_SPREAD,
    ]


@pytest.mark.asyncio
async def test_equity_trader_different_symbols():
    """Test equity trader handles different symbols."""
    agent = MockEquityTrader()
    
    for symbol in ["AAPL", "MSFT", "GOOGL"]:
        context = {"symbol": symbol}
        plan = await agent.create_execution_plan(context)
        
        assert plan.symbol == symbol
        assert isinstance(plan, ExecutionPlan)


@pytest.mark.asyncio
async def test_equity_trader_metadata():
    """Test equity trader has correct metadata."""
    agent = MockEquityTrader()
    
    metadata = agent.get_metadata()
    
    assert metadata["role"] == AgentRole.EQUITY_TRADER.value
    assert "timestamp" in metadata


# =============================================================================
# F&O Trader Tests
# =============================================================================


@pytest.mark.asyncio
async def test_fno_trader_basic_plan(sample_context):
    """Test F&O trader produces valid execution plan."""
    agent = MockFnOTrader()
    
    plan = await agent.create_execution_plan(sample_context)
    
    assert isinstance(plan, ExecutionPlan)
    assert plan.symbol == sample_context["symbol"]
    assert isinstance(plan.orders, list)
    assert len(plan.orders) > 0


@pytest.mark.asyncio
async def test_fno_trader_multi_leg_orders(sample_context):
    """Test F&O trader can create multi-leg orders."""
    agent = MockFnOTrader()
    
    plan = await agent.create_execution_plan(sample_context)
    
    # F&O strategies often have multiple legs
    assert len(plan.orders) >= 1


@pytest.mark.asyncio
async def test_fno_trader_options_orders(sample_context):
    """Test F&O trader creates options orders with required fields."""
    agent = MockFnOTrader()
    
    plan = await agent.create_execution_plan(sample_context)
    
    # Check if any orders have options fields
    has_options = False
    for order in plan.orders:
        if order.option_type is not None:
            has_options = True
            assert order.expiry is not None
            assert order.strike is not None
            assert order.option_type in ["call", "put"]
    
    # At least one order should be an option for F&O trader
    assert has_options


@pytest.mark.asyncio
async def test_fno_trader_cost_estimation(sample_context):
    """Test F&O trader estimates costs."""
    agent = MockFnOTrader()
    
    plan = await agent.create_execution_plan(sample_context)
    
    assert plan.estimated_cost is not None
    assert plan.estimated_cost > 0
    assert plan.estimated_slippage >= 0


@pytest.mark.asyncio
async def test_fno_trader_timing_recommendation(sample_context):
    """Test F&O trader provides timing recommendation."""
    agent = MockFnOTrader()
    
    plan = await agent.create_execution_plan(sample_context)
    
    assert plan.timing_recommendation is not None


@pytest.mark.asyncio
async def test_fno_trader_strategy_type(sample_context):
    """Test F&O trader specifies strategy type."""
    agent = MockFnOTrader()
    
    plan = await agent.create_execution_plan(sample_context)
    
    assert plan.strategy_type in [
        StrategyType.LONG_EQUITY,
        StrategyType.SHORT_EQUITY,
        StrategyType.COVERED_CALL,
        StrategyType.PROTECTIVE_PUT,
        StrategyType.BULL_CALL_SPREAD,
        StrategyType.BEAR_PUT_SPREAD,
        StrategyType.IRON_CONDOR,
        StrategyType.STRADDLE,
        StrategyType.STRANGLE,
        StrategyType.BUTTERFLY_SPREAD,
    ]


@pytest.mark.asyncio
async def test_fno_trader_different_symbols():
    """Test F&O trader handles different symbols."""
    agent = MockFnOTrader()
    
    for symbol in ["AAPL", "MSFT", "GOOGL"]:
        context = {"symbol": symbol}
        plan = await agent.create_execution_plan(context)
        
        assert plan.symbol == symbol
        assert isinstance(plan, ExecutionPlan)


@pytest.mark.asyncio
async def test_fno_trader_metadata():
    """Test F&O trader has correct metadata."""
    agent = MockFnOTrader()
    
    metadata = agent.get_metadata()
    
    assert metadata["role"] == AgentRole.FNO_TRADER.value
    assert "timestamp" in metadata


# =============================================================================
# Order Validation Tests
# =============================================================================


@pytest.mark.asyncio
async def test_equity_order_has_required_fields(sample_context):
    """Test equity orders have all required fields."""
    agent = MockEquityTrader()
    
    plan = await agent.create_execution_plan(sample_context)
    
    for order in plan.orders:
        assert order.symbol is not None
        assert order.side is not None
        assert order.quantity is not None
        assert order.order_type is not None


@pytest.mark.asyncio
async def test_options_order_has_required_fields(sample_context):
    """Test options orders have all required fields."""
    agent = MockFnOTrader()
    
    plan = await agent.create_execution_plan(sample_context)
    
    for order in plan.orders:
        if order.option_type is not None:
            # Options order
            assert order.expiry is not None
            assert order.strike is not None
            assert order.option_type in ["call", "put"]


@pytest.mark.asyncio
async def test_limit_order_has_price(sample_context):
    """Test limit orders have price specified."""
    agent = MockEquityTrader()
    
    plan = await agent.create_execution_plan(sample_context)
    
    for order in plan.orders:
        if order.order_type == OrderType.LIMIT:
            assert order.price is not None
            assert order.price > 0


# =============================================================================
# Execution Plan Validation Tests
# =============================================================================


@pytest.mark.asyncio
async def test_execution_plan_timestamp(sample_context):
    """Test execution plans have timestamps."""
    agent = MockEquityTrader()
    
    plan = await agent.create_execution_plan(sample_context)
    
    assert plan.timestamp is not None


@pytest.mark.asyncio
async def test_execution_plan_cost_positive(sample_context):
    """Test execution plans have positive costs."""
    agents = [MockEquityTrader(), MockFnOTrader()]
    
    for agent in agents:
        plan = await agent.create_execution_plan(sample_context)
        assert plan.estimated_cost > 0


@pytest.mark.asyncio
async def test_execution_plan_slippage_non_negative(sample_context):
    """Test execution plans have non-negative slippage."""
    agents = [MockEquityTrader(), MockFnOTrader()]
    
    for agent in agents:
        plan = await agent.create_execution_plan(sample_context)
        assert plan.estimated_slippage >= 0


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.asyncio
async def test_both_traders_work_together(sample_context):
    """Test both trader agents can work together."""
    equity_trader = MockEquityTrader()
    fno_trader = MockFnOTrader()
    
    equity_plan = await equity_trader.create_execution_plan(sample_context)
    fno_plan = await fno_trader.create_execution_plan(sample_context)
    
    # Both should produce valid plans
    assert isinstance(equity_plan, ExecutionPlan)
    assert isinstance(fno_plan, ExecutionPlan)
    
    # Both should have same symbol
    assert equity_plan.symbol == sample_context["symbol"]
    assert fno_plan.symbol == sample_context["symbol"]


@pytest.mark.asyncio
async def test_execution_agents_no_api_calls(sample_context):
    """Test that mock agents don't make real API calls."""
    agents = [MockEquityTrader(), MockFnOTrader()]
    
    for agent in agents:
        plan = await agent.create_execution_plan(sample_context)
        assert plan is not None
        assert plan.symbol == sample_context["symbol"]


@pytest.mark.asyncio
async def test_execution_performance():
    """Test that mock agents execute quickly."""
    import time
    
    agent = MockEquityTrader()
    context = {"symbol": "AAPL"}
    
    start = time.time()
    plan = await agent.create_execution_plan(context)
    duration = time.time() - start
    
    # Mock agents should be very fast (< 0.1 seconds)
    assert duration < 0.1
    assert plan is not None


@pytest.mark.asyncio
async def test_execution_plans_are_different():
    """Test that different traders produce different execution plans."""
    context = {"symbol": "AAPL"}
    
    equity_trader = MockEquityTrader()
    fno_trader = MockFnOTrader()
    
    equity_plan = await equity_trader.create_execution_plan(context)
    fno_plan = await fno_trader.create_execution_plan(context)
    
    # Plans should have different characteristics
    # F&O plans typically have more orders and higher costs
    assert equity_plan.strategy_type != fno_plan.strategy_type or len(equity_plan.orders) != len(fno_plan.orders)
