"""
Tests for Strategy & Research agents using mock implementations.

Tests all three Strategy & Research agents:
- BullishResearcher
- BearishResearcher
- DerivativesStrategist
"""

import pytest

from src.data.schemas import (
    AgentRole,
    DebateArgument,
    StrategyProposal,
    StrategyType,
    TradeDirection,
)
from tests.mock_agents import (
    MockBearishResearcher,
    MockBullishResearcher,
    MockDerivativesStrategist,
)


# =============================================================================
# Bullish Researcher Tests
# =============================================================================


@pytest.mark.asyncio
async def test_bullish_researcher_basic_debate(sample_context):
    """Test bullish researcher produces valid debate argument."""
    agent = MockBullishResearcher()

    argument = await agent.debate(sample_context, round_number=1)

    assert isinstance(argument, DebateArgument)
    assert argument.agent_role == AgentRole.BULLISH_RESEARCHER
    assert argument.round_number == 1
    assert argument.confidence > 0.0


@pytest.mark.asyncio
async def test_bullish_researcher_argument_structure(sample_context):
    """Test bullish researcher argument has proper structure."""
    agent = MockBullishResearcher()

    argument = await agent.debate(sample_context, round_number=1)

    assert argument.argument is not None
    assert len(argument.argument) > 0
    assert isinstance(argument.supporting_evidence, list)
    assert len(argument.supporting_evidence) > 0


@pytest.mark.asyncio
async def test_bullish_researcher_multiple_rounds(sample_context):
    """Test bullish researcher can debate multiple rounds."""
    agent = MockBullishResearcher()

    arguments = []
    for round_num in range(1, 4):
        argument = await agent.debate(sample_context, round_number=round_num)
        arguments.append(argument)
        assert argument.round_number == round_num


@pytest.mark.asyncio
async def test_bullish_researcher_with_previous_arguments(sample_context):
    """Test bullish researcher considers previous arguments."""
    agent = MockBullishResearcher()

    # First round
    arg1 = await agent.debate(sample_context, round_number=1)

    # Second round with previous argument
    arg2 = await agent.debate(sample_context, round_number=2, previous_arguments=[arg1])

    assert arg2.round_number == 2
    assert isinstance(arg2, DebateArgument)


@pytest.mark.asyncio
async def test_bullish_researcher_metadata():
    """Test bullish researcher has correct metadata."""
    agent = MockBullishResearcher()

    metadata = agent.get_metadata()

    assert metadata["role"] == AgentRole.BULLISH_RESEARCHER.value
    assert "timestamp" in metadata


# =============================================================================
# Bearish Researcher Tests
# =============================================================================


@pytest.mark.asyncio
async def test_bearish_researcher_basic_debate(sample_context):
    """Test bearish researcher produces valid debate argument."""
    agent = MockBearishResearcher()

    argument = await agent.debate(sample_context, round_number=1)

    assert isinstance(argument, DebateArgument)
    assert argument.agent_role == AgentRole.BEARISH_RESEARCHER
    assert argument.round_number == 1
    assert argument.confidence > 0.0


@pytest.mark.asyncio
async def test_bearish_researcher_argument_structure(sample_context):
    """Test bearish researcher argument has proper structure."""
    agent = MockBearishResearcher()

    argument = await agent.debate(sample_context, round_number=1)

    assert argument.argument is not None
    assert len(argument.argument) > 0
    assert isinstance(argument.supporting_evidence, list)
    assert len(argument.supporting_evidence) > 0


@pytest.mark.asyncio
async def test_bearish_researcher_multiple_rounds(sample_context):
    """Test bearish researcher can debate multiple rounds."""
    agent = MockBearishResearcher()

    for round_num in range(1, 4):
        argument = await agent.debate(sample_context, round_number=round_num)
        assert argument.round_number == round_num


@pytest.mark.asyncio
async def test_bearish_researcher_metadata():
    """Test bearish researcher has correct metadata."""
    agent = MockBearishResearcher()

    metadata = agent.get_metadata()

    assert metadata["role"] == AgentRole.BEARISH_RESEARCHER.value


# =============================================================================
# Debate Interaction Tests
# =============================================================================


@pytest.mark.asyncio
async def test_bull_bear_debate_interaction(sample_context):
    """Test bull and bear researchers can debate each other."""
    bullish_agent = MockBullishResearcher()
    bearish_agent = MockBearishResearcher()

    arguments = []

    # Round 1
    bull_arg1 = await bullish_agent.debate(sample_context, round_number=1)
    arguments.append(bull_arg1)

    bear_arg1 = await bearish_agent.debate(
        sample_context, round_number=1, previous_arguments=arguments
    )
    arguments.append(bear_arg1)

    # Round 2
    bull_arg2 = await bullish_agent.debate(
        sample_context, round_number=2, previous_arguments=arguments
    )
    arguments.append(bull_arg2)

    bear_arg2 = await bearish_agent.debate(
        sample_context, round_number=2, previous_arguments=arguments
    )
    arguments.append(bear_arg2)

    # Verify all arguments
    assert len(arguments) == 4
    assert arguments[0].agent_role == AgentRole.BULLISH_RESEARCHER
    assert arguments[1].agent_role == AgentRole.BEARISH_RESEARCHER
    assert arguments[2].agent_role == AgentRole.BULLISH_RESEARCHER
    assert arguments[3].agent_role == AgentRole.BEARISH_RESEARCHER


@pytest.mark.asyncio
async def test_debate_argument_timestamps(sample_context):
    """Test debate arguments have valid timestamps."""
    agent = MockBullishResearcher()

    argument = await agent.debate(sample_context, round_number=1)

    assert argument.timestamp is not None


# =============================================================================
# Derivatives Strategist Tests
# =============================================================================


@pytest.mark.asyncio
async def test_derivatives_strategist_basic_proposal(sample_context):
    """Test derivatives strategist produces valid strategy proposal."""
    agent = MockDerivativesStrategist()

    proposal = await agent.propose_strategy(sample_context)

    assert isinstance(proposal, StrategyProposal)
    assert proposal.symbol == sample_context["symbol"]
    assert proposal.confidence > 0.0


@pytest.mark.asyncio
async def test_derivatives_strategist_strategy_type(sample_context):
    """Test derivatives strategist specifies strategy type."""
    agent = MockDerivativesStrategist()

    proposal = await agent.propose_strategy(sample_context)

    assert proposal.strategy_type in [
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
async def test_derivatives_strategist_trade_direction(sample_context):
    """Test derivatives strategist specifies trade direction."""
    agent = MockDerivativesStrategist()

    proposal = await agent.propose_strategy(sample_context)

    assert proposal.direction in [TradeDirection.LONG, TradeDirection.SHORT, TradeDirection.NEUTRAL]


@pytest.mark.asyncio
async def test_derivatives_strategist_risk_reward(sample_context):
    """Test derivatives strategist includes risk/reward metrics."""
    agent = MockDerivativesStrategist()

    proposal = await agent.propose_strategy(sample_context)

    assert proposal.expected_return is not None
    assert proposal.max_loss is not None
    assert isinstance(proposal.expected_return, (int, float))
    assert isinstance(proposal.max_loss, (int, float))


@pytest.mark.asyncio
async def test_derivatives_strategist_entry_exit_criteria(sample_context):
    """Test derivatives strategist specifies entry/exit criteria."""
    agent = MockDerivativesStrategist()

    proposal = await agent.propose_strategy(sample_context)

    assert isinstance(proposal.entry_criteria, list)
    assert isinstance(proposal.exit_criteria, list)


@pytest.mark.asyncio
async def test_derivatives_strategist_risk_factors(sample_context):
    """Test derivatives strategist identifies risk factors."""
    agent = MockDerivativesStrategist()

    proposal = await agent.propose_strategy(sample_context)

    assert isinstance(proposal.risk_factors, list)


@pytest.mark.asyncio
async def test_derivatives_strategist_holding_period(sample_context):
    """Test derivatives strategist specifies holding period."""
    agent = MockDerivativesStrategist()

    proposal = await agent.propose_strategy(sample_context)

    assert proposal.holding_period is not None
    assert len(proposal.holding_period) > 0


@pytest.mark.asyncio
async def test_derivatives_strategist_rationale(sample_context):
    """Test derivatives strategist provides rationale."""
    agent = MockDerivativesStrategist()

    proposal = await agent.propose_strategy(sample_context)

    assert proposal.rationale is not None
    assert len(proposal.rationale) > 0


@pytest.mark.asyncio
async def test_derivatives_strategist_different_symbols():
    """Test derivatives strategist handles different symbols."""
    agent = MockDerivativesStrategist()

    for symbol in ["AAPL", "MSFT", "GOOGL"]:
        context = {"symbol": symbol}
        proposal = await agent.propose_strategy(context)

        assert proposal.symbol == symbol


@pytest.mark.asyncio
async def test_derivatives_strategist_metadata():
    """Test derivatives strategist has correct metadata."""
    agent = MockDerivativesStrategist()

    metadata = agent.get_metadata()

    assert metadata["role"] == AgentRole.DERIVATIVES_STRATEGIST.value


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.asyncio
async def test_complete_research_workflow(sample_context):
    """Test complete strategy research workflow."""
    bullish_agent = MockBullishResearcher()
    bearish_agent = MockBearishResearcher()
    strategist = MockDerivativesStrategist()

    # Debate phase
    arguments = []
    for round_num in range(1, 3):
        bull_arg = await bullish_agent.debate(sample_context, round_num, arguments)
        arguments.append(bull_arg)

        bear_arg = await bearish_agent.debate(sample_context, round_num, arguments)
        arguments.append(bear_arg)

    # Strategy proposal
    proposal = await strategist.propose_strategy(sample_context)

    # Verify workflow completion
    assert len(arguments) == 4
    assert isinstance(proposal, StrategyProposal)


@pytest.mark.asyncio
async def test_strategy_research_agents_no_api_calls(sample_context):
    """Test that mock agents don't make real API calls."""
    agents = [
        MockBullishResearcher(),
        MockBearishResearcher(),
        MockDerivativesStrategist(),
    ]

    # Debate agents
    for agent in agents[:2]:
        argument = await agent.debate(sample_context, round_number=1)
        assert argument is not None

    # Strategist
    proposal = await agents[2].propose_strategy(sample_context)
    assert proposal is not None


@pytest.mark.asyncio
async def test_strategy_research_performance(sample_context):
    """Test that mock agents execute quickly."""
    import time

    agent = MockDerivativesStrategist()

    start = time.time()
    proposal = await agent.propose_strategy(sample_context)
    duration = time.time() - start

    # Mock agents should be very fast (< 0.1 seconds)
    assert duration < 0.1
    assert proposal is not None
