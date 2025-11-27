"""Tests for Deep Reasoner v2.0 agents.

This module tests the new DeepSeek R1, Janus-Pro, and FinRL agents.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.strategy_research.reasoning import DeepSeekReasoningAgent
from src.agents.market_intelligence.vision import JanusVisualAnalyst
from src.agents.execution.rl_executor import FinRLExecutionAgent
from src.data.schemas import (
    AgentRole,
    DeepSeekReasoningReport,
    JanusVisualReport,
    FinRLExecutionReport,
    StrategyProposal,
    TradeDirection,
    TechnicalReport,
    FundamentalsReport,
    TrendDirection,
    Sentiment,
)


# =============================================================================
# DeepSeek Reasoning Agent Tests
# =============================================================================


class TestDeepSeekReasoningAgent:
    """Tests for DeepSeek R1 Reasoning Agent."""

    @pytest.fixture
    def agent(self):
        """Create a DeepSeek Reasoning Agent instance."""
        with patch("src.agents.base.create_llm") as mock_create_llm:
            mock_llm = MagicMock()
            mock_create_llm.return_value = mock_llm
            return DeepSeekReasoningAgent()

    @pytest.fixture
    def sample_strategy_proposal(self):
        """Create a sample strategy proposal for testing."""
        return StrategyProposal(
            symbol="AAPL",
            strategy_type="LONG_EQUITY",
            direction=TradeDirection.LONG,
            rationale="Strong fundamentals support long position",
            expected_return=12.0,
            max_loss=-8.0,
            entry_conditions=["Price above 180", "RSI < 70"],
            exit_conditions=["Target reached", "Stop loss hit"],
            position_size_pct=0.03,
            time_horizon_days=45,
        )

    @pytest.fixture
    def sample_context(self, sample_strategy_proposal):
        """Create sample context for testing."""
        return {
            "symbol": "AAPL",
            "strategy_proposal": sample_strategy_proposal,
            "analyst_reports": {
                "technical": TechnicalReport(
                    symbol="AAPL",
                    summary="Bullish trend",
                    confidence=0.75,
                    trend_direction=TrendDirection.UPTREND,
                ),
                "fundamentals": FundamentalsReport(
                    symbol="AAPL",
                    summary="Strong fundamentals",
                    confidence=0.8,
                    investment_thesis=Sentiment.BULLISH,
                ),
            },
        }

    def test_agent_initialization(self, agent):
        """Test agent is properly initialized."""
        assert agent.role == AgentRole.DEEPSEEK_REASONING_AGENT
        assert agent.temperature == 0.3

    def test_agent_has_correct_role(self, agent):
        """Test agent has the correct role."""
        assert agent.role.value == "deepseek_reasoning_agent"

    @pytest.mark.asyncio
    async def test_analyze_without_strategy(self, agent):
        """Test analyze returns error when no strategy provided."""
        result = await agent.analyze({"symbol": "AAPL"})

        assert isinstance(result, DeepSeekReasoningReport)
        assert result.strategy_validated is False
        assert result.approval_status == "rejected"

    @pytest.mark.asyncio
    async def test_build_validation_prompt(self, agent, sample_context):
        """Test validation prompt is built correctly."""
        prompt = agent._build_validation_prompt(sample_context)

        assert "AAPL" in prompt
        assert "LONG_EQUITY" in prompt
        assert "12.0%" in prompt
        assert "VALIDATION TASKS" in prompt

    def test_parse_validation_response_valid_json(self, agent):
        """Test parsing valid JSON response."""
        response = """
        ```json
        {
            "strategy_validated": true,
            "approval_status": "approved",
            "mathematical_analysis": "Risk/reward is favorable",
            "risk_metrics": {"risk_reward_ratio": 1.5},
            "confidence_score": 0.8,
            "summary": "Strategy is valid"
        }
        ```
        """

        result = agent._parse_validation_response("AAPL", response, "reasoning trace")

        assert result.strategy_validated is True
        assert result.approval_status == "approved"
        assert result.confidence == 0.8

    def test_parse_validation_response_invalid_json(self, agent):
        """Test parsing invalid JSON falls back gracefully."""
        response = "This is not valid JSON"

        result = agent._parse_validation_response("AAPL", response, "")

        assert isinstance(result, DeepSeekReasoningReport)
        assert result.strategy_validated is False


# =============================================================================
# Janus Visual Analyst Tests
# =============================================================================


class TestJanusVisualAnalyst:
    """Tests for Janus-Pro Visual Analyst."""

    @pytest.fixture
    def agent(self):
        """Create a Janus Visual Analyst instance."""
        with patch("src.agents.base.create_llm") as mock_create_llm:
            mock_llm = MagicMock()
            mock_create_llm.return_value = mock_llm
            return JanusVisualAnalyst()

    def test_agent_initialization(self, agent):
        """Test agent is properly initialized."""
        assert agent.role == AgentRole.JANUS_VISUAL_ANALYST
        assert agent.temperature == 0.4

    def test_agent_has_correct_role(self, agent):
        """Test agent has the correct role."""
        assert agent.role.value == "janus_visual_analyst"

    @pytest.mark.asyncio
    async def test_analyze_without_image(self, agent):
        """Test analyze returns error when no image available."""
        result = await agent.analyze({"symbol": "AAPL"})

        assert isinstance(result, JanusVisualReport)
        assert result.confidence == 0.0
        assert "No chart image" in result.summary

    @pytest.mark.asyncio
    async def test_get_chart_image_none(self, agent):
        """Test _get_chart_image returns None when no source available."""
        result = await agent._get_chart_image({})
        assert result is None

    @pytest.mark.asyncio
    async def test_get_chart_image_from_context(self, agent):
        """Test _get_chart_image returns image from context."""
        result = await agent._get_chart_image({"chart_image": "base64data"})
        assert result == "base64data"

    def test_parse_janus_response(self, agent):
        """Test parsing Janus API response."""
        result = {
            "patterns": [
                {"name": "Double Top", "confidence": 0.8, "stage": "complete"}
            ],
            "confidence": 0.75,
            "summary": "Bearish pattern detected",
            "description": "Full description",
            "trend": "bearish",
            "levels": {"support": [180.0], "resistance": [200.0]},
            "confluence": ["MACD divergence"],
            "implications": "Consider short positions",
        }

        report = agent._parse_janus_response("AAPL", result, "chart_data")

        assert len(report.patterns_detected) == 1
        assert report.confidence == 0.75
        assert report.trend_analysis == "bearish"


# =============================================================================
# FinRL Execution Agent Tests
# =============================================================================


class TestFinRLExecutionAgent:
    """Tests for FinRL Execution Agent."""

    @pytest.fixture
    def agent(self):
        """Create a FinRL Execution Agent instance."""
        with patch("src.agents.base.create_llm") as mock_create_llm:
            mock_llm = MagicMock()
            mock_create_llm.return_value = mock_llm
            return FinRLExecutionAgent()

    @pytest.fixture
    def sample_strategy(self):
        """Create sample strategy for testing."""
        return StrategyProposal(
            symbol="AAPL",
            strategy_type="LONG_EQUITY",
            direction=TradeDirection.LONG,
            rationale="Test strategy",
            expected_return=10.0,
            max_loss=-5.0,
            position_size_pct=0.02,
        )

    def test_agent_initialization(self, agent):
        """Test agent is properly initialized."""
        assert agent.role == AgentRole.FINRL_EXECUTION_AGENT
        assert agent.temperature == 0.2
        assert agent._last_r1_signal == 0.0
        assert agent._last_janus_confidence == 0.0

    def test_agent_has_correct_role(self, agent):
        """Test agent has the correct role."""
        assert agent.role.value == "finrl_execution_agent"

    def test_update_strategic_signals(self, agent):
        """Test updating strategic signals from slow loops."""
        agent.update_strategic_signals(r1_signal=0.7, janus_confidence=0.85)

        assert agent._last_r1_signal == 0.7
        assert agent._last_janus_confidence == 0.85

    def test_build_state_vector(self, agent, sample_strategy):
        """Test building state vector for RL agent."""
        context = {
            "current_price": 195.0,
            "bid": 194.9,
            "ask": 195.1,
            "volume": 1000000,
            "technical_indicators": {"rsi": 65.0, "macd": 0.5},
            "strategy_proposal": sample_strategy,
        }

        state = agent._build_state_vector(context)

        assert state["price"] == 195.0
        assert state["rsi"] == 65.0
        assert state["strategy_direction"] == 1.0  # Long
        assert "combined_signal" in state

    @pytest.mark.asyncio
    async def test_rule_based_execution_buy(self, agent, sample_strategy):
        """Test rule-based execution for buy signal."""
        state = {
            "combined_signal": 0.6,
            "strategy_direction": 1.0,
            "r1_sentiment": 0.5,
            "janus_pattern_confidence": 0.7,
            "spread": 0.1,
            "price": 195.0,
        }

        result = await agent._rule_based_execution("AAPL", state, {"strategy_proposal": sample_strategy})

        assert result.action_type == "buy"
        assert result.execution_confidence > 0.5

    @pytest.mark.asyncio
    async def test_rule_based_execution_sell(self, agent, sample_strategy):
        """Test rule-based execution for sell signal."""
        state = {
            "combined_signal": -0.6,
            "strategy_direction": -1.0,
            "r1_sentiment": -0.5,
            "janus_pattern_confidence": 0.3,
            "spread": 0.1,
            "price": 195.0,
        }

        result = await agent._rule_based_execution("AAPL", state, {"strategy_proposal": sample_strategy})

        assert result.action_type == "sell"

    @pytest.mark.asyncio
    async def test_rule_based_execution_hold(self, agent, sample_strategy):
        """Test rule-based execution for hold signal."""
        state = {
            "combined_signal": 0.1,
            "strategy_direction": 0.0,
            "r1_sentiment": 0.0,
            "janus_pattern_confidence": 0.5,
            "spread": 0.1,
            "price": 195.0,
        }

        result = await agent._rule_based_execution("AAPL", state, {"strategy_proposal": sample_strategy})

        assert result.action_type == "hold"


# =============================================================================
# Integration Tests
# =============================================================================


class TestDeepReasonerIntegration:
    """Integration tests for Deep Reasoner v2.0 agents."""

    def test_all_agents_have_unique_roles(self):
        """Test all Deep Reasoner agents have unique roles."""
        roles = [
            AgentRole.DEEPSEEK_REASONING_AGENT,
            AgentRole.JANUS_VISUAL_ANALYST,
            AgentRole.FINRL_EXECUTION_AGENT,
        ]

        assert len(roles) == len(set(roles))

    def test_report_schemas_are_valid(self):
        """Test all new report schemas can be instantiated."""
        reasoning_report = DeepSeekReasoningReport(
            symbol="AAPL",
            summary="Test",
            confidence=0.8,
        )
        assert reasoning_report.agent_role == AgentRole.DEEPSEEK_REASONING_AGENT

        visual_report = JanusVisualReport(
            symbol="AAPL",
            summary="Test",
            confidence=0.7,
        )
        assert visual_report.agent_role == AgentRole.JANUS_VISUAL_ANALYST

        execution_report = FinRLExecutionReport(
            symbol="AAPL",
            summary="Test",
            confidence=0.6,
        )
        assert execution_report.agent_role == AgentRole.FINRL_EXECUTION_AGENT
