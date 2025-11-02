"""
Base agent class for Project Shri Sudarshan.

This module defines the abstract base class that all agents inherit from.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

from ..config import settings
from ..data.schemas import AgentReport, AgentRole


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
    ):
        """
        Initialize the base agent.
        
        Args:
            role: The role of this agent
            system_prompt: The system prompt defining agent behavior
            model_name: LLM model to use (defaults to standard_model from settings)
            temperature: Temperature for LLM generation
        """
        self.role = role
        self.system_prompt = system_prompt
        self.temperature = temperature
        
        # Select model based on importance
        if model_name is None:
            model_name = settings.standard_model
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=settings.openai_api_key,
        )
        
        # Create prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        
    @abstractmethod
    async def analyze(self, context: Dict[str, Any]) -> AgentReport:
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
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this agent.
        
        Returns:
            Dict with agent metadata
        """
        return {
            "role": self.role.value,
            "model": self.llm.model_name,
            "temperature": self.temperature,
            "timestamp": datetime.now().isoformat(),
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(role={self.role.value})"


class CriticalAgent(BaseAgent):
    """
    Base class for critical decision-making agents.
    
    These agents use the premium model (GPT-4o) by default.
    """
    
    def __init__(
        self,
        role: AgentRole,
        system_prompt: str,
        temperature: float = 0.7,
    ):
        """Initialize critical agent with premium model."""
        super().__init__(
            role=role,
            system_prompt=system_prompt,
            model_name=settings.premium_model,
            temperature=temperature,
        )
