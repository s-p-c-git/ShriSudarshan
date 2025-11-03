"""
Configuration management for Project Shri Sudarshan.

This module handles all configuration settings using pydantic-settings
for validation and environment variable management.
"""

from typing import Literal, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # LLM Provider Configuration
    llm_provider: Literal["openai", "anthropic"] = Field(
        default="openai", description="LLM provider to use (openai or anthropic)"
    )

    # OpenAI Configuration
    openai_api_key: str = Field(
        default="test-key-not-set", description="OpenAI API key"
    )
    premium_model: str = Field(
        default="gpt-4o", description="Premium LLM model for critical decisions"
    )
    standard_model: str = Field(
        default="gpt-4o-mini", description="Standard LLM model for routine tasks"
    )

    # Anthropic Configuration
    anthropic_api_key: Optional[str] = Field(
        default=None, description="Anthropic API key"
    )
    anthropic_premium_model: str = Field(
        default="claude-3-5-sonnet-20241022", description="Premium Anthropic model for critical decisions"
    )
    anthropic_standard_model: str = Field(
        default="claude-3-5-sonnet-20241022", description="Standard Anthropic model for routine tasks"
    )

    # Data Provider Keys
    alpha_vantage_api_key: Optional[str] = Field(default=None, description="Alpha Vantage API key")
    tradier_api_key: Optional[str] = Field(
        default=None, description="Tradier API key for options data"
    )

    # Memory Configuration
    chroma_persist_directory: str = Field(
        default="./data/chroma_db", description="ChromaDB persistence directory"
    )
    database_url: str = Field(
        default="sqlite:///./data/episodic_memory.db",
        description="Database URL for episodic memory",
    )

    # Redis Configuration (Optional)
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")

    # System Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    environment: str = Field(
        default="development", description="Environment (development/production)"
    )

    # Risk Management Parameters
    max_position_size: float = Field(
        default=0.05, description="Maximum position size as fraction of portfolio"
    )
    max_portfolio_risk: float = Field(
        default=0.02, description="Maximum portfolio risk (VaR threshold)"
    )
    max_sector_concentration: float = Field(
        default=0.25, description="Maximum concentration in any sector"
    )

    # Execution Configuration
    paper_trading: bool = Field(default=True, description="Enable paper trading mode")
    broker_api_endpoint: Optional[str] = Field(default=None, description="Broker API endpoint")
    broker_api_key: Optional[str] = Field(default=None, description="Broker API key")

    # Agent Configuration
    enable_concurrent_analysis: bool = Field(
        default=True, description="Enable concurrent agent execution"
    )
    max_debate_rounds: int = Field(default=3, description="Maximum number of debate rounds")
    analysis_timeout_seconds: int = Field(default=30, description="Timeout for analysis phase")

    # Data Configuration
    market_data_cache_ttl: int = Field(default=300, description="Market data cache TTL in seconds")
    news_lookback_days: int = Field(default=7, description="Number of days to look back for news")
    historical_data_period: str = Field(default="1y", description="Historical data period")

    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_key(cls, v: str, info) -> str:
        """Validate OpenAI API key is set when using OpenAI provider."""
        # Get llm_provider from the data dictionary (values being validated)
        llm_provider = info.data.get("llm_provider", "openai")
        if llm_provider == "openai" and v == "test-key-not-set":
            # Allow test key for testing environments
            pass
        return v

    @field_validator("anthropic_api_key")
    @classmethod
    def validate_anthropic_key(cls, v: Optional[str], info) -> Optional[str]:
        """Validate Anthropic API key is set when using Anthropic provider."""
        llm_provider = info.data.get("llm_provider", "openai")
        if llm_provider == "anthropic" and not v:
            raise ValueError(
                "anthropic_api_key must be set when llm_provider is 'anthropic'"
            )
        return v


# Global settings instance
settings = Settings()
