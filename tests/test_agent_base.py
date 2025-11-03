"""Test agent base classes with multiple LLM providers."""

import os
from unittest.mock import AsyncMock, Mock, patch

import pytest
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from src.agents.base import BaseAgent, CriticalAgent, create_llm
from src.config.settings import Settings
from src.data.schemas import AgentReport, AgentRole


# ============================================================================
# Test LLM Factory
# ============================================================================


def test_create_llm_openai_default():
    """Test creating OpenAI LLM with default settings."""
    with patch("src.agents.base.settings") as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.standard_model = "gpt-4o-mini"
        mock_settings.openai_api_key = "test-key"

        llm = create_llm()

        assert isinstance(llm, ChatOpenAI)
        assert llm.model_name == "gpt-4o-mini"
        assert llm.temperature == 0.7


def test_create_llm_openai_custom_model():
    """Test creating OpenAI LLM with custom model."""
    with patch("src.agents.base.settings") as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.openai_api_key = "test-key"

        llm = create_llm(model_name="gpt-4o", temperature=0.5)

        assert isinstance(llm, ChatOpenAI)
        assert llm.model_name == "gpt-4o"
        assert llm.temperature == 0.5


def test_create_llm_anthropic_default():
    """Test creating Anthropic LLM with default settings."""
    with patch("src.agents.base.settings") as mock_settings:
        mock_settings.llm_provider = "anthropic"
        mock_settings.anthropic_standard_model = "claude-3-5-sonnet-20241022"
        mock_settings.anthropic_api_key = "test-anthropic-key"

        llm = create_llm()

        assert isinstance(llm, ChatAnthropic)
        assert llm.model == "claude-3-5-sonnet-20241022"
        assert llm.temperature == 0.7


def test_create_llm_anthropic_custom_model():
    """Test creating Anthropic LLM with custom model."""
    with patch("src.agents.base.settings") as mock_settings:
        mock_settings.llm_provider = "anthropic"
        mock_settings.anthropic_api_key = "test-anthropic-key"

        llm = create_llm(
            model_name="claude-3-5-sonnet-20241022",
            temperature=0.3,
        )

        assert isinstance(llm, ChatAnthropic)
        assert llm.model == "claude-3-5-sonnet-20241022"
        assert llm.temperature == 0.3


def test_create_llm_anthropic_missing_key():
    """Test that creating Anthropic LLM without API key raises error."""
    with patch("src.agents.base.settings") as mock_settings:
        mock_settings.llm_provider = "anthropic"
        mock_settings.anthropic_api_key = None

        with pytest.raises(ValueError, match="anthropic_api_key must be set"):
            create_llm()


def test_create_llm_unsupported_provider():
    """Test that unsupported provider raises error."""
    with patch("src.agents.base.settings") as mock_settings:
        mock_settings.llm_provider = "unsupported"

        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            create_llm()


def test_create_llm_explicit_provider_override():
    """Test that explicit provider parameter overrides settings."""
    with patch("src.agents.base.settings") as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.anthropic_api_key = "test-anthropic-key"
        mock_settings.anthropic_standard_model = "claude-3-5-sonnet-20241022"

        # Request anthropic explicitly even though settings default to openai
        llm = create_llm(provider="anthropic")

        assert isinstance(llm, ChatAnthropic)


# ============================================================================
# Test Configuration Settings
# ============================================================================


def test_settings_default_provider():
    """Test that default provider is OpenAI."""
    settings = Settings(_env_file=None, openai_api_key="test-key")  # Don't load from file
    assert settings.llm_provider == "openai"


def test_settings_anthropic_provider():
    """Test Anthropic provider configuration."""
    settings = Settings(
        _env_file=None, llm_provider="anthropic", anthropic_api_key="test-anthropic-key"
    )
    assert settings.llm_provider == "anthropic"
    assert settings.anthropic_api_key == "test-anthropic-key"


def test_settings_anthropic_without_key_fails(monkeypatch):
    """Test that using Anthropic without API key raises validation error."""
    # Clear the ANTHROPIC_API_KEY environment variable set in conftest.py
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ValidationError, match="anthropic_api_key must be set"):
        Settings(_env_file=None, llm_provider="anthropic", openai_api_key="test-key")


def test_settings_anthropic_models():
    """Test Anthropic model configuration."""
    settings = Settings(
        _env_file=None,
        llm_provider="anthropic",
        anthropic_api_key="test-key",
        anthropic_premium_model="claude-3-5-sonnet-20241022",
        anthropic_standard_model="claude-3-5-sonnet-20241022",
    )
    assert settings.anthropic_premium_model == "claude-3-5-sonnet-20241022"
    assert settings.anthropic_standard_model == "claude-3-5-sonnet-20241022"


# ============================================================================
# Test BaseAgent
# ============================================================================


class MockAgent(BaseAgent):
    """Concrete agent implementation for testing."""

    async def analyze(self, context: dict) -> AgentReport:
        """Simple analysis implementation."""
        return AgentReport(
            role=self.role,
            symbol=context.get("symbol", "TEST"),
            summary="Test analysis",
            confidence=0.8,
        )


@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    mock = AsyncMock()
    mock_response = Mock()
    mock_response.content = "Test response"
    mock.ainvoke.return_value = mock_response
    return mock


def test_base_agent_openai_initialization():
    """Test BaseAgent initialization with OpenAI."""
    with patch("src.agents.base.settings") as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.standard_model = "gpt-4o-mini"
        mock_settings.openai_api_key = "test-key"

        agent = MockAgent(role=AgentRole.FUNDAMENTALS_ANALYST, system_prompt="Test prompt")

        assert agent.role == AgentRole.FUNDAMENTALS_ANALYST
        assert agent.system_prompt == "Test prompt"
        assert agent.provider == "openai"
        assert isinstance(agent.llm, ChatOpenAI)


def test_base_agent_anthropic_initialization():
    """Test BaseAgent initialization with Anthropic."""
    with patch("src.agents.base.settings") as mock_settings:
        mock_settings.llm_provider = "anthropic"
        mock_settings.anthropic_standard_model = "claude-3-5-sonnet-20241022"
        mock_settings.anthropic_api_key = "test-anthropic-key"

        agent = MockAgent(role=AgentRole.FUNDAMENTALS_ANALYST, system_prompt="Test prompt")

        assert agent.role == AgentRole.FUNDAMENTALS_ANALYST
        assert agent.provider == "anthropic"
        assert isinstance(agent.llm, ChatAnthropic)


def test_base_agent_explicit_provider():
    """Test BaseAgent with explicit provider override."""
    with patch("src.agents.base.settings") as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.anthropic_api_key = "test-anthropic-key"
        mock_settings.anthropic_standard_model = "claude-3-5-sonnet-20241022"

        # Force use of Anthropic
        agent = MockAgent(
            role=AgentRole.FUNDAMENTALS_ANALYST, system_prompt="Test prompt", provider="anthropic"
        )

        assert agent.provider == "anthropic"
        assert isinstance(agent.llm, ChatAnthropic)


@pytest.mark.asyncio
async def test_base_agent_generate_response():
    """Test agent response generation."""
    with patch("src.agents.base.settings") as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.standard_model = "gpt-4o-mini"
        mock_settings.openai_api_key = "test-key"

        agent = MockAgent(role=AgentRole.FUNDAMENTALS_ANALYST, system_prompt="Test prompt")

        # Mock the LLM with AsyncMock for ainvoke method
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_llm = Mock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        with patch.object(agent, "llm", new=mock_llm):
            response = await agent._generate_response("test input")

            assert response == "Test response"
            mock_llm.ainvoke.assert_called_once()


def test_base_agent_get_metadata():
    """Test agent metadata."""
    with patch("src.agents.base.settings") as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.standard_model = "gpt-4o-mini"
        mock_settings.openai_api_key = "test-key"

        agent = MockAgent(role=AgentRole.FUNDAMENTALS_ANALYST, system_prompt="Test prompt")

        metadata = agent.get_metadata()

        assert metadata["role"] == AgentRole.FUNDAMENTALS_ANALYST.value
        assert "model" in metadata
        assert metadata["temperature"] == 0.7
        assert "timestamp" in metadata


# ============================================================================
# Test CriticalAgent
# ============================================================================


class MockCriticalAgent(CriticalAgent):
    """Concrete critical agent for testing."""

    async def analyze(self, context: dict) -> AgentReport:
        """Simple analysis implementation."""
        return AgentReport(
            role=self.role,
            symbol=context.get("symbol", "TEST"),
            summary="Critical analysis",
            confidence=0.9,
        )


def test_critical_agent_openai_uses_premium():
    """Test CriticalAgent uses premium OpenAI model."""
    with patch("src.agents.base.settings") as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.premium_model = "gpt-4o"
        mock_settings.openai_api_key = "test-key"

        agent = MockCriticalAgent(role=AgentRole.PORTFOLIO_MANAGER, system_prompt="Critical prompt")

        assert isinstance(agent.llm, ChatOpenAI)
        assert agent.llm.model_name == "gpt-4o"


def test_critical_agent_anthropic_uses_premium():
    """Test CriticalAgent uses premium Anthropic model."""
    with patch("src.agents.base.settings") as mock_settings:
        mock_settings.llm_provider = "anthropic"
        mock_settings.anthropic_premium_model = "claude-3-5-sonnet-20241022"
        mock_settings.anthropic_api_key = "test-anthropic-key"

        agent = MockCriticalAgent(role=AgentRole.PORTFOLIO_MANAGER, system_prompt="Critical prompt")

        assert isinstance(agent.llm, ChatAnthropic)
        assert agent.llm.model == "claude-3-5-sonnet-20241022"


def test_critical_agent_explicit_provider():
    """Test CriticalAgent with explicit provider override."""
    with patch("src.agents.base.settings") as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.premium_model = "gpt-4o"
        mock_settings.anthropic_premium_model = "claude-3-5-sonnet-20241022"
        mock_settings.anthropic_api_key = "test-anthropic-key"

        # Force use of Anthropic
        agent = MockCriticalAgent(
            role=AgentRole.PORTFOLIO_MANAGER, system_prompt="Critical prompt", provider="anthropic"
        )

        assert agent.provider == "anthropic"
        assert isinstance(agent.llm, ChatAnthropic)


# ============================================================================
# Test Mixed Provider Scenarios
# ============================================================================


def test_mixed_providers_same_workflow():
    """Test using both OpenAI and Anthropic in the same workflow."""
    with patch("src.agents.base.settings") as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.standard_model = "gpt-4o-mini"
        mock_settings.premium_model = "gpt-4o"
        mock_settings.anthropic_standard_model = "claude-3-5-sonnet-20241022"
        mock_settings.anthropic_premium_model = "claude-3-5-sonnet-20241022"
        mock_settings.openai_api_key = "test-openai-key"
        mock_settings.anthropic_api_key = "test-anthropic-key"

        # Create agent with default provider (OpenAI)
        agent1 = MockAgent(role=AgentRole.FUNDAMENTALS_ANALYST, system_prompt="Test prompt 1")

        # Create agent explicitly using Anthropic
        agent2 = MockAgent(
            role=AgentRole.TECHNICAL_ANALYST, system_prompt="Test prompt 2", provider="anthropic"
        )

        # Create critical agent with Anthropic
        agent3 = MockCriticalAgent(
            role=AgentRole.PORTFOLIO_MANAGER, system_prompt="Critical prompt", provider="anthropic"
        )

        assert isinstance(agent1.llm, ChatOpenAI)
        assert isinstance(agent2.llm, ChatAnthropic)
        assert isinstance(agent3.llm, ChatAnthropic)
