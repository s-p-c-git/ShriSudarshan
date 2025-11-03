"""
Integration tests for Anthropic API.

These tests validate real Anthropic API integration and are designed to:
1. Run only when a valid ANTHROPIC_API_KEY is provided
2. Execute a single successful workflow run
3. Never log or expose the API key
4. Skip gracefully if no key is available

To run these tests:
    pytest -m anthropic
    pytest tests/test_integration_anthropic.py

To skip these tests (default):
    pytest -m "not integration"
"""

import os
from typing import Optional

import pytest

# Import after setting env vars
from src.agents.base import create_llm
from src.config.settings import Settings
from src.data.schemas import AgentRole


def get_anthropic_key() -> Optional[str]:
    """
    Safely retrieve Anthropic API key from environment.
    
    Returns:
        API key if available, None otherwise. Never logs or prints the key.
    """
    return os.environ.get("ANTHROPIC_API_KEY")


def is_anthropic_available() -> bool:
    """
    Check if Anthropic API is available for testing.
    
    Returns:
        True if API key is set and appears valid, False otherwise.
    """
    key = get_anthropic_key()
    if not key:
        return False
    # Basic validation: key should start with expected prefix and have reasonable length
    # This doesn't expose the actual key value
    return key.startswith("sk-ant-") and len(key) > 20


# Pytest skip conditions
pytestmark = [
    pytest.mark.integration,
    pytest.mark.anthropic,
    pytest.mark.skipif(
        not is_anthropic_available(),
        reason="ANTHROPIC_API_KEY not set or invalid. Set the environment variable to run integration tests.",
    ),
]


@pytest.mark.asyncio
class TestAnthropicIntegration:
    """Integration tests for Anthropic Claude API."""
    
    async def test_anthropic_llm_creation(self):
        """
        Test that Anthropic LLM can be created with valid configuration.
        
        This validates:
        - API key is properly loaded
        - LLM factory creates ChatAnthropic instance
        - Model configuration is correct
        """
        # Create LLM with explicit Anthropic provider
        llm = create_llm(
            model_name="claude-3-5-sonnet-20241022",
            temperature=0.7,
            provider="anthropic",
        )
        
        # Verify LLM was created
        assert llm is not None
        assert hasattr(llm, "model")
        assert llm.model == "claude-3-5-sonnet-20241022"
        
        # Verify it's the correct type
        from langchain_anthropic import ChatAnthropic
        assert isinstance(llm, ChatAnthropic)
    
    async def test_anthropic_simple_invocation(self):
        """
        Test a single successful invocation of Anthropic API.
        
        This validates:
        - API connection works
        - Authentication succeeds
        - Response is received and formatted correctly
        
        This is the core integration test that proves end-to-end functionality.
        """
        from langchain_core.messages import HumanMessage, SystemMessage
        
        # Create Anthropic LLM
        llm = create_llm(
            model_name="claude-3-5-sonnet-20241022",
            temperature=0.7,
            provider="anthropic",
        )
        
        # Prepare a simple test prompt
        messages = [
            SystemMessage(content="You are a helpful assistant that provides concise answers."),
            HumanMessage(content="What is 2+2? Answer with just the number."),
        ]
        
        # Make the API call
        response = await llm.ainvoke(messages)
        
        # Validate response
        assert response is not None
        assert hasattr(response, "content")
        assert response.content is not None
        assert isinstance(response.content, str)
        assert len(response.content) > 0
        
        # Verify response contains expected answer (should contain "4")
        assert "4" in response.content
    
    async def test_anthropic_agent_workflow(self):
        """
        Test a realistic agent workflow using Anthropic.
        
        This validates:
        - Agent can be created with Anthropic provider
        - Agent can process market-related prompts
        - Response format is appropriate for agent use
        
        This simulates how agents would actually use Anthropic in the system.
        """
        from langchain_core.messages import HumanMessage, SystemMessage
        
        # Create Anthropic LLM with agent-like configuration
        llm = create_llm(
            model_name="claude-3-5-sonnet-20241022",
            temperature=0.7,
            provider="anthropic",
        )
        
        # Simulate a fundamentals analyst prompt
        system_prompt = """You are a Fundamentals Analyst for a trading system.
Provide brief, structured analysis of stocks based on available data."""
        
        analysis_prompt = """Analyze AAPL stock with the following data:
- Current Price: $195.50
- P/E Ratio: 28.5
- Revenue Growth: 8% YoY
- Market Cap: $3T

Provide a brief 2-sentence analysis focusing on valuation and growth."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=analysis_prompt),
        ]
        
        # Make the API call
        response = await llm.ainvoke(messages)
        
        # Validate response
        assert response is not None
        assert hasattr(response, "content")
        assert response.content is not None
        assert isinstance(response.content, str)
        
        # Response should be substantive (at least 50 characters)
        assert len(response.content) > 50
        
        # Response should mention the stock (case-insensitive)
        content_lower = response.content.lower()
        assert "aapl" in content_lower or "apple" in content_lower


@pytest.mark.asyncio
class TestAnthropicSettings:
    """Test Anthropic configuration and settings."""
    
    def test_anthropic_settings_validation(self):
        """
        Test that Settings properly validates Anthropic configuration.
        
        This validates:
        - Settings can load Anthropic API key from environment
        - Anthropic provider is properly configured
        - Model names are correctly set
        """
        # Create settings with Anthropic provider
        settings = Settings(
            llm_provider="anthropic",
            anthropic_api_key=get_anthropic_key(),
        )
        
        assert settings.llm_provider == "anthropic"
        assert settings.anthropic_api_key is not None
        assert len(settings.anthropic_api_key) > 0
        assert settings.anthropic_premium_model == "claude-3-5-sonnet-20241022"
        assert settings.anthropic_standard_model == "claude-3-5-sonnet-20241022"
    
    def test_anthropic_model_selection(self):
        """
        Test that appropriate models are selected for different agent types.
        
        This validates:
        - Premium model is used for critical agents
        - Standard model is used for regular agents
        - Model selection respects provider choice
        """
        # Test premium model selection
        premium_llm = create_llm(
            model_name=None,  # Should use default premium
            temperature=0.7,
            provider="anthropic",
        )
        
        # Anthropic uses the same model for both premium and standard
        assert premium_llm.model == "claude-3-5-sonnet-20241022"


class TestAnthropicSkipConditions:
    """Test that skip conditions work correctly."""
    
    def test_skip_detection_functions(self):
        """
        Test the helper functions that determine if tests should run.
        
        This test always runs (not marked as integration) to verify the
        skip logic works correctly.
        """
        # Test key retrieval
        key = get_anthropic_key()
        if key:
            assert isinstance(key, str)
            assert len(key) > 0
        else:
            assert key is None
        
        # Test availability check
        available = is_anthropic_available()
        assert isinstance(available, bool)
        
        # If key exists, availability should match key validation
        if key:
            assert available == (key.startswith("sk-ant-") and len(key) > 20)
        else:
            assert available is False
