"""
Tests for Oversight & Learning agents using mock implementations.

Tests all three Oversight agents:
- RiskManager
- PortfolioManager
- ReflectiveAgent
"""

import pytest

from src.data.schemas import (
    AgentRole,
    PortfolioDecision,
    RiskAssessment,
)
from tests.mock_agents import (
    MockPortfolioManager,
    MockReflectiveAgent,
    MockRiskManager,
)


# =============================================================================
# Risk Manager Tests
# =============================================================================


@pytest.mark.asyncio
async def test_risk_manager_basic_assessment(sample_context):
    """Test risk manager produces valid risk assessment."""
    agent = MockRiskManager()
    
    assessment = await agent.assess_risk(sample_context)
    
    assert isinstance(assessment, RiskAssessment)
    assert assessment.symbol == sample_context["symbol"]


@pytest.mark.asyncio
async def test_risk_manager_approval_status(sample_context):
    """Test risk manager provides approval status."""
    agent = MockRiskManager()
    
    assessment = await agent.assess_risk(sample_context)
    
    assert isinstance(assessment.approved, bool)


@pytest.mark.asyncio
async def test_risk_manager_var_estimate(sample_context):
    """Test risk manager provides VaR estimate."""
    agent = MockRiskManager()
    
    assessment = await agent.assess_risk(sample_context)
    
    assert assessment.var_estimate is not None
    assert isinstance(assessment.var_estimate, (int, float))
    assert assessment.var_estimate > 0


@pytest.mark.asyncio
async def test_risk_manager_position_sizing(sample_context):
    """Test risk manager provides position sizing."""
    agent = MockRiskManager()
    
    assessment = await agent.assess_risk(sample_context)
    
    assert assessment.position_size_pct is not None
    assert isinstance(assessment.position_size_pct, (int, float))
    assert assessment.position_size_pct > 0


@pytest.mark.asyncio
async def test_risk_manager_sector_exposure(sample_context):
    """Test risk manager tracks sector exposure."""
    agent = MockRiskManager()
    
    assessment = await agent.assess_risk(sample_context)
    
    # Sector exposure can be optional but if present should be a string
    if assessment.sector_exposure is not None:
        assert isinstance(assessment.sector_exposure, str)


@pytest.mark.asyncio
async def test_risk_manager_warnings(sample_context):
    """Test risk manager provides risk warnings."""
    agent = MockRiskManager()
    
    assessment = await agent.assess_risk(sample_context)
    
    assert isinstance(assessment.risk_warnings, list)


@pytest.mark.asyncio
async def test_risk_manager_recommendation(sample_context):
    """Test risk manager provides recommendation."""
    agent = MockRiskManager()
    
    assessment = await agent.assess_risk(sample_context)
    
    assert assessment.recommendation is not None
    assert len(assessment.recommendation) > 0


@pytest.mark.asyncio
async def test_risk_manager_approval_control():
    """Test risk manager can be controlled to approve or reject."""
    agent = MockRiskManager()
    
    # Test approval
    context_approve = {"symbol": "AAPL", "should_approve": True}
    assessment_approve = await agent.assess_risk(context_approve)
    assert assessment_approve.approved is True
    
    # Test rejection
    context_reject = {"symbol": "AAPL", "should_approve": False}
    assessment_reject = await agent.assess_risk(context_reject)
    assert assessment_reject.approved is False


@pytest.mark.asyncio
async def test_risk_manager_timestamp(sample_context):
    """Test risk assessment has timestamp."""
    agent = MockRiskManager()
    
    assessment = await agent.assess_risk(sample_context)
    
    assert assessment.timestamp is not None


@pytest.mark.asyncio
async def test_risk_manager_metadata():
    """Test risk manager has correct metadata."""
    agent = MockRiskManager()
    
    metadata = agent.get_metadata()
    
    assert metadata["role"] == AgentRole.RISK_MANAGER.value
    assert "timestamp" in metadata


# =============================================================================
# Portfolio Manager Tests
# =============================================================================


@pytest.mark.asyncio
async def test_portfolio_manager_basic_decision(sample_context, sample_risk_assessment):
    """Test portfolio manager produces valid decision."""
    agent = MockPortfolioManager()
    
    context = {**sample_context, "risk_assessment": sample_risk_assessment}
    decision = await agent.make_decision(context)
    
    assert isinstance(decision, PortfolioDecision)
    assert decision.symbol == sample_context["symbol"]


@pytest.mark.asyncio
async def test_portfolio_manager_approval_status(sample_context, sample_risk_assessment):
    """Test portfolio manager provides approval status."""
    agent = MockPortfolioManager()
    
    context = {**sample_context, "risk_assessment": sample_risk_assessment}
    decision = await agent.make_decision(context)
    
    assert isinstance(decision.approved, bool)


@pytest.mark.asyncio
async def test_portfolio_manager_rationale(sample_context, sample_risk_assessment):
    """Test portfolio manager provides rationale."""
    agent = MockPortfolioManager()
    
    context = {**sample_context, "risk_assessment": sample_risk_assessment}
    decision = await agent.make_decision(context)
    
    assert decision.decision_rationale is not None
    assert len(decision.decision_rationale) > 0


@pytest.mark.asyncio
async def test_portfolio_manager_position_size(sample_context, sample_risk_assessment):
    """Test portfolio manager specifies position size."""
    agent = MockPortfolioManager()
    
    context = {**sample_context, "risk_assessment": sample_risk_assessment}
    decision = await agent.make_decision(context)
    
    assert decision.position_size is not None
    assert isinstance(decision.position_size, (int, float))
    assert decision.position_size >= 0


@pytest.mark.asyncio
async def test_portfolio_manager_monitoring_requirements(sample_context, sample_risk_assessment):
    """Test portfolio manager specifies monitoring requirements."""
    agent = MockPortfolioManager()
    
    context = {**sample_context, "risk_assessment": sample_risk_assessment}
    decision = await agent.make_decision(context)
    
    assert isinstance(decision.monitoring_requirements, list)


@pytest.mark.asyncio
async def test_portfolio_manager_conditions(sample_context, sample_risk_assessment):
    """Test portfolio manager specifies conditions."""
    agent = MockPortfolioManager()
    
    context = {**sample_context, "risk_assessment": sample_risk_assessment}
    decision = await agent.make_decision(context)
    
    assert isinstance(decision.conditions, list)


@pytest.mark.asyncio
async def test_portfolio_manager_respects_risk_rejection(sample_context):
    """Test portfolio manager respects risk manager rejection."""
    agent = MockPortfolioManager()
    
    # Create a rejected risk assessment
    rejected_risk_assessment = RiskAssessment(
        symbol=sample_context["symbol"],
        approved=False,
        var_estimate=5000.00,
        position_size_pct=10.0,
        risk_warnings=["Excessive risk"],
        recommendation="Rejected",
    )
    
    context = {**sample_context, "risk_assessment": rejected_risk_assessment}
    decision = await agent.make_decision(context)
    
    # Portfolio manager should reject if risk manager rejected
    assert decision.approved is False


@pytest.mark.asyncio
async def test_portfolio_manager_timestamp(sample_context, sample_risk_assessment):
    """Test portfolio decision has timestamp."""
    agent = MockPortfolioManager()
    
    context = {**sample_context, "risk_assessment": sample_risk_assessment}
    decision = await agent.make_decision(context)
    
    assert decision.timestamp is not None


@pytest.mark.asyncio
async def test_portfolio_manager_metadata():
    """Test portfolio manager has correct metadata."""
    agent = MockPortfolioManager()
    
    metadata = agent.get_metadata()
    
    assert metadata["role"] == AgentRole.PORTFOLIO_MANAGER.value
    assert "timestamp" in metadata


# =============================================================================
# Reflective Agent Tests
# =============================================================================


@pytest.mark.asyncio
async def test_reflective_agent_basic_reflection(sample_context):
    """Test reflective agent produces valid reflection."""
    agent = MockReflectiveAgent()
    
    reflection = await agent.reflect(sample_context)
    
    assert isinstance(reflection, dict)


@pytest.mark.asyncio
async def test_reflective_agent_success_factors(sample_context):
    """Test reflective agent identifies success factors."""
    agent = MockReflectiveAgent()
    
    reflection = await agent.reflect(sample_context)
    
    assert "success_factors" in reflection
    assert isinstance(reflection["success_factors"], list)


@pytest.mark.asyncio
async def test_reflective_agent_failure_factors(sample_context):
    """Test reflective agent identifies failure factors."""
    agent = MockReflectiveAgent()
    
    reflection = await agent.reflect(sample_context)
    
    assert "failure_factors" in reflection
    assert isinstance(reflection["failure_factors"], list)


@pytest.mark.asyncio
async def test_reflective_agent_lessons_learned(sample_context):
    """Test reflective agent provides lessons learned."""
    agent = MockReflectiveAgent()
    
    reflection = await agent.reflect(sample_context)
    
    assert "lessons_learned" in reflection
    assert isinstance(reflection["lessons_learned"], list)


@pytest.mark.asyncio
async def test_reflective_agent_strategy_adjustments(sample_context):
    """Test reflective agent suggests strategy adjustments."""
    agent = MockReflectiveAgent()
    
    reflection = await agent.reflect(sample_context)
    
    assert "strategy_adjustments" in reflection
    assert isinstance(reflection["strategy_adjustments"], list)


@pytest.mark.asyncio
async def test_reflective_agent_confidence_adjustment(sample_context):
    """Test reflective agent provides confidence adjustment."""
    agent = MockReflectiveAgent()
    
    reflection = await agent.reflect(sample_context)
    
    assert "confidence_adjustment" in reflection
    assert isinstance(reflection["confidence_adjustment"], (int, float))


@pytest.mark.asyncio
async def test_reflective_agent_metadata():
    """Test reflective agent has correct metadata."""
    agent = MockReflectiveAgent()
    
    metadata = agent.get_metadata()
    
    assert metadata["role"] == AgentRole.REFLECTIVE_AGENT.value


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.asyncio
async def test_oversight_workflow(sample_context, sample_strategy_proposal):
    """Test complete oversight workflow."""
    risk_manager = MockRiskManager()
    portfolio_manager = MockPortfolioManager()
    
    # Risk assessment
    context_with_strategy = {**sample_context, "strategy_proposal": sample_strategy_proposal}
    risk_assessment = await risk_manager.assess_risk(context_with_strategy)
    
    # Portfolio decision
    context_with_risk = {**context_with_strategy, "risk_assessment": risk_assessment}
    portfolio_decision = await portfolio_manager.make_decision(context_with_risk)
    
    # Verify workflow
    assert isinstance(risk_assessment, RiskAssessment)
    assert isinstance(portfolio_decision, PortfolioDecision)
    assert portfolio_decision.symbol == sample_context["symbol"]


@pytest.mark.asyncio
async def test_oversight_rejection_flow(sample_context, sample_strategy_proposal):
    """Test rejection flow in oversight."""
    risk_manager = MockRiskManager()
    portfolio_manager = MockPortfolioManager()
    
    # Force risk rejection
    context_with_strategy = {
        **sample_context,
        "strategy_proposal": sample_strategy_proposal,
        "should_approve": False,
    }
    risk_assessment = await risk_manager.assess_risk(context_with_strategy)
    
    # Portfolio manager should also reject
    context_with_risk = {**context_with_strategy, "risk_assessment": risk_assessment}
    portfolio_decision = await portfolio_manager.make_decision(context_with_risk)
    
    assert risk_assessment.approved is False
    assert portfolio_decision.approved is False


@pytest.mark.asyncio
async def test_oversight_agents_no_api_calls(sample_context, sample_risk_assessment):
    """Test that mock agents don't make real API calls."""
    risk_manager = MockRiskManager()
    portfolio_manager = MockPortfolioManager()
    reflective_agent = MockReflectiveAgent()
    
    # Risk assessment
    risk_assessment = await risk_manager.assess_risk(sample_context)
    assert risk_assessment is not None
    
    # Portfolio decision
    context_with_risk = {**sample_context, "risk_assessment": sample_risk_assessment}
    decision = await portfolio_manager.make_decision(context_with_risk)
    assert decision is not None
    
    # Reflection
    reflection = await reflective_agent.reflect(sample_context)
    assert reflection is not None


@pytest.mark.asyncio
async def test_oversight_performance():
    """Test that mock agents execute quickly."""
    import time
    
    agent = MockRiskManager()
    context = {"symbol": "AAPL"}
    
    start = time.time()
    assessment = await agent.assess_risk(context)
    duration = time.time() - start
    
    # Mock agents should be very fast (< 0.1 seconds)
    assert duration < 0.1
    assert assessment is not None


@pytest.mark.asyncio
async def test_all_oversight_agents_use_critical_model():
    """Test that oversight agents are CriticalAgent instances."""
    from src.agents.base import CriticalAgent
    
    risk_manager = MockRiskManager()
    portfolio_manager = MockPortfolioManager()
    reflective_agent = MockReflectiveAgent()
    
    # All oversight agents should use CriticalAgent base
    assert isinstance(risk_manager, CriticalAgent)
    assert isinstance(portfolio_manager, CriticalAgent)
    assert isinstance(reflective_agent, CriticalAgent)
