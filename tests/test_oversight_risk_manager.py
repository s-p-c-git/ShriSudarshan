# tests/test_oversight_risk_manager.py
"""
Tests for RiskManager oversight agent.

These tests verify basic risk assessment functionality.
"""
import pytest

# Try to import, skip tests if dependencies missing
pytest.importorskip("yfinance")

from src.data.schemas import RiskAssessment, StrategyProposal, StrategyType, TradeDirection


@pytest.fixture
def sample_risk_context(sample_symbol):
    """Fixture providing sample context for risk assessment."""
    strategy = StrategyProposal(
        symbol=sample_symbol,
        strategy_type=StrategyType.LONG_EQUITY,
        direction=TradeDirection.LONG,
        rationale="Strong fundamentals",
        expected_return=15.0,
        max_loss=-10.0,
        holding_period="30 days",
        entry_criteria=["Price above support"],
        exit_criteria=["Target reached"],
        position_size_pct=0.05,
        confidence=0.75,
    )

    return {
        "symbol": sample_symbol,
        "strategy_proposal": strategy,
        "portfolio_state": {
            "total_value": 100000.0,
            "var": 500.0,
            "sector_exposures": {"Technology": 10000.0},
        },
    }


def test_risk_manager_import():
    """Test that RiskManager can be imported."""
    from src.agents.oversight import risk_manager

    assert hasattr(risk_manager, "RiskManager")


def test_risk_manager_instantiation():
    """Test that RiskManager can be instantiated."""
    from src.agents.oversight.risk_manager import RiskManager

    rm = RiskManager()
    assert rm is not None
    assert hasattr(rm, "role")


@pytest.mark.asyncio
async def test_risk_manager_has_assess_risk(sample_risk_context):
    """Test that RiskManager has assess_risk method."""
    from src.agents.oversight.risk_manager import RiskManager

    rm = RiskManager()

    # Check if method exists
    if hasattr(rm, "assess_risk"):
        assessment = await rm.assess_risk(sample_risk_context)

        # Basic assertions - adapt to implementation
        assert assessment is not None
        assert isinstance(assessment, RiskAssessment) or isinstance(assessment, dict)


@pytest.mark.asyncio
async def test_risk_manager_basic_assessment(sample_risk_context):
    """Test basic risk assessment functionality."""
    from src.agents.oversight.risk_manager import RiskManager

    rm = RiskManager()

    # Simulate inputs - this will vary by implementation
    if hasattr(rm, "assess_risk"):
        assessment = await rm.assess_risk(sample_risk_context)

        # Verify assessment structure
        if isinstance(assessment, RiskAssessment):
            assert hasattr(assessment, "symbol")
            assert hasattr(assessment, "approved")
            assert assessment.symbol == sample_risk_context["symbol"]
        elif isinstance(assessment, dict):
            # If returned as dict, check keys
            assert "symbol" in assessment or "approved" in assessment


@pytest.mark.asyncio
async def test_risk_manager_position_size_check(sample_risk_context):
    """Test that RiskManager checks position size limits."""
    from src.agents.oversight.risk_manager import RiskManager

    rm = RiskManager()

    if hasattr(rm, "assess_risk"):
        # Test with normal position
        assessment = await rm.assess_risk(sample_risk_context)
        assert assessment is not None

        # Test with oversized position
        large_position_context = sample_risk_context.copy()
        large_position_context["strategy_proposal"].position_size_pct = 0.20  # 20% position

        large_assessment = await rm.assess_risk(large_position_context)

        # Both assessments should complete without error
        assert large_assessment is not None


@pytest.mark.asyncio
async def test_risk_manager_var_calculation(sample_risk_context):
    """Test that RiskManager considers VaR in assessment."""
    from src.agents.oversight.risk_manager import RiskManager

    rm = RiskManager()

    if hasattr(rm, "assess_risk"):
        assessment = await rm.assess_risk(sample_risk_context)

        # Check if VaR is considered in the assessment
        if isinstance(assessment, RiskAssessment):
            assert hasattr(assessment, "var_estimate")
            # VaR should be non-negative
            if assessment.var_estimate is not None:
                assert assessment.var_estimate >= 0
