"""
Base agent class for Project Shri Sudarshan.

This module defines the abstract base class that all agents inherit from.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional, Union

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..config import settings
from ..data.schemas import AgentReport, AgentRole


def create_llm(
    model_name: Optional[str] = None,
    temperature: float = 0.7,
    provider: Optional[str] = None,
) -> Union[ChatOpenAI, ChatAnthropic]:
    """
    Factory function to create an LLM instance based on the configured provider.

    Args:
        model_name: Specific model to use (overrides defaults)
        temperature: Temperature for LLM generation
        provider: LLM provider to use (overrides settings.llm_provider)

    Returns:
        ChatOpenAI or ChatAnthropic instance

    Raises:
        ValueError: If provider is not supported or API key is missing

    Note:
        For DeepSeek provider, uses OpenAI SDK with custom base_url.
        SECURITY: Do NOT install 'deepseek' or 'deepseeek' packages from PyPI.
    """
    llm_provider = provider or settings.llm_provider

    if llm_provider == "openai":
        # Use provided model or default to standard model
        if model_name is None:
            model_name = settings.standard_model

        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=settings.openai_api_key,
        )
    elif llm_provider == "anthropic":
        # Use provided model or default to standard model
        if model_name is None:
            model_name = settings.anthropic_standard_model

        if not settings.anthropic_api_key:
            raise ValueError("anthropic_api_key must be set when using Anthropic provider")

        return ChatAnthropic(
            model=model_name,
            temperature=temperature,
            anthropic_api_key=settings.anthropic_api_key,
        )
    elif llm_provider == "deepseek":
        # DeepSeek uses OpenAI SDK with custom base_url
        # SECURITY: Using OpenAI SDK, NOT malicious PyPI packages
        if model_name is None:
            model_name = settings.deepseek_chat_model

        if not settings.deepseek_api_key:
            raise ValueError("deepseek_api_key must be set when using DeepSeek provider")

        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.

    All agents inherit from this class and implement the analyze method.
    Agents can use different LLM models based on their importance.
    """

    def __init__(
        self,
        role: AgentRole,
        system_prompt: str,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        provider: Optional[str] = None,
    ):
        """
        Initialize the base agent.

        Args:
            role: The role of this agent
            system_prompt: The system prompt defining agent behavior
            model_name: LLM model to use (defaults to standard_model from settings)
            temperature: Temperature for LLM generation
            provider: LLM provider to use (defaults to settings.llm_provider)
        """
        self.role = role
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.provider = provider or settings.llm_provider

        # Initialize LLM using factory function
        self.llm = create_llm(
            model_name=model_name,
            temperature=temperature,
            provider=self.provider,
        )

        # Create prompt template
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )

    @abstractmethod
    async def analyze(self, context: dict[str, Any]) -> AgentReport:
        """
        Perform analysis based on the given context.

        This method must be implemented by all subclasses.

        Args:
            context: Dictionary containing analysis context (symbol, data, etc.)

        Returns:
            AgentReport: Structured report from the agent
        """
        pass

    async def _generate_response(self, input_text: str) -> str:
        """
        Generate a response using the LLM.

        Args:
            input_text: The input prompt text

        Returns:
            str: Generated response
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=input_text),
        ]

        response = await self.llm.ainvoke(messages)
        return response.content

    def get_metadata(self) -> dict[str, Any]:
        """
        Get metadata about this agent.

        Returns:
            Dict with agent metadata
        """
        # Handle different attribute names for different LLM providers
        model_name = getattr(self.llm, "model_name", None) or getattr(self.llm, "model", "unknown")

        return {
            "role": self.role.value,
            "model": model_name,
            "temperature": self.temperature,
            "timestamp": datetime.now().isoformat(),
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(role={self.role.value})"


class CriticalAgent(BaseAgent):
    """
    Base class for critical decision-making agents.

    These agents use the premium model (GPT-4o or Claude 3.5 Sonnet) by default.
    """

    def __init__(
        self,
        role: AgentRole,
        system_prompt: str,
        temperature: float = 0.7,
        provider: Optional[str] = None,
    ):
        """Initialize critical agent with premium model."""
        llm_provider = provider or settings.llm_provider

        # Select premium model based on provider
        if llm_provider == "openai":
            premium_model = settings.premium_model
        else:  # anthropic
            premium_model = settings.anthropic_premium_model

        super().__init__(
            role=role,
            system_prompt=system_prompt,
            model_name=premium_model,
            temperature=temperature,
            provider=provider,
        )
