"""
Data schemas for Project Shri Sudarshan.

This module defines all Pydantic models and enums used throughout the system.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, root_validator


# =============================================================================
# Enums
# =============================================================================


class AgentRole(str, Enum):
    """Enumeration of agent roles in the system."""

    FUNDAMENTALS_ANALYST = "fundamentals_analyst"
    TECHNICAL_ANALYST = "technical_analyst"
    SENTIMENT_ANALYST = "sentiment_analyst"
    MACRO_NEWS_ANALYST = "macro_news_analyst"
    FINBERT_SENTIMENT_ANALYST = "finbert_sentiment_analyst"
    FINGPT_GENERATIVE_ANALYST = "fingpt_generative_analyst"
    BULLISH_RESEARCHER = "bullish_researcher"
    BEARISH_RESEARCHER = "bearish_researcher"
    DERIVATIVES_STRATEGIST = "derivatives_strategist"
    EQUITY_TRADER = "equity_trader"
    FNO_TRADER = "fno_trader"
    RISK_MANAGER = "risk_manager"
    PORTFOLIO_MANAGER = "portfolio_manager"
    REFLECTIVE_AGENT = "reflective_agent"


class Sentiment(str, Enum):
    """Enumeration of sentiment values."""

    VERY_BEARISH = "very_bearish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    BULLISH = "bullish"
    VERY_BULLISH = "very_bullish"


class TrendDirection(str, Enum):
    """Enumeration of trend directions."""

    STRONG_DOWNTREND = "strong_downtrend"
    DOWNTREND = "downtrend"
    SIDEWAYS = "sideways"
    UPTREND = "uptrend"
    STRONG_UPTREND = "strong_uptrend"


class StrategyType(str, Enum):
    """Enumeration of trading strategy types."""

    LONG_EQUITY = "long_equity"
    SHORT_EQUITY = "short_equity"
    COVERED_CALL = "covered_call"
    PROTECTIVE_PUT = "protective_put"
    BULL_CALL_SPREAD = "bull_call_spread"
    BEAR_PUT_SPREAD = "bear_put_spread"
    IRON_CONDOR = "iron_condor"
    STRADDLE = "straddle"
    STRANGLE = "strangle"
    BUTTERFLY_SPREAD = "butterfly_spread"


class TradeDirection(str, Enum):
    """Enumeration of trade directions."""

    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"


class OrderSide(str, Enum):
    """Enumeration of order sides."""

    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """Enumeration of order types."""

    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


# =============================================================================
# Base Models
# =============================================================================


class AgentReport(BaseModel):
    """Base class for all agent reports."""

    model_config = ConfigDict(use_enum_values=True)

    agent_role: AgentRole
    symbol: str
    summary: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @root_validator(pre=True)
    def accept_legacy_fields(cls, values):
        """
        Compatibility shim to accept legacy field names:
         - 'confidence_level' (1-10 scale) -> 'confidence' (0.0-1.0)
         - 'analysis' -> 'summary'
        This allows older call sites to keep working while we migrate the codebase.
        """
        # Map 'analysis' -> 'summary'
        if "summary" not in values and "analysis" in values:
            values["summary"] = values.pop("analysis")

        # Map 'confidence_level' -> 'confidence'
        if "confidence" not in values and "confidence_level" in values:
            try:
                raw = values.pop("confidence_level")
                # If integer 1-10, convert to 0.0-1.0
                if isinstance(raw, (int, float)) and raw > 1:
                    values["confidence"] = float(raw) / 10.0
                else:
                    values["confidence"] = float(raw)
            except Exception:
                values["confidence"] = 0.5

        return values


# =============================================================================
# Market Intelligence Reports
# =============================================================================


class FundamentalsReport(AgentReport):
    """Report from Fundamentals Analyst."""

    agent_role: AgentRole = Field(default=AgentRole.FUNDAMENTALS_ANALYST)
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    intrinsic_value: Optional[float] = None
    current_price: Optional[float] = None
    investment_thesis: Sentiment = Field(default=Sentiment.NEUTRAL)


class TechnicalReport(AgentReport):
    """Report from Technical Analyst."""

    agent_role: AgentRole = Field(default=AgentRole.TECHNICAL_ANALYST)
    trend_direction: TrendDirection = Field(default=TrendDirection.SIDEWAYS)
    support_levels: list[float] = Field(default_factory=list)
    resistance_levels: list[float] = Field(default_factory=list)
    chart_patterns: list[str] = Field(default_factory=list)
    indicators: dict[str, Any] = Field(default_factory=dict)
    volatility: Optional[float] = None


class SentimentReport(AgentReport):
    """Report from Sentiment Analyst."""

    agent_role: AgentRole = Field(default=AgentRole.SENTIMENT_ANALYST)
    social_sentiment: Sentiment = Field(default=Sentiment.NEUTRAL)
    sentiment_score: float = Field(default=0.0, ge=-1.0, le=1.0)
    volume_trend: Optional[str] = None
    retail_interest: Optional[str] = None
    institutional_activity: Optional[str] = None


class MacroNewsReport(AgentReport):
    """Report from Macro/News Analyst."""

    agent_role: AgentRole = Field(default=AgentRole.MACRO_NEWS_ANALYST)
    market_sentiment: Sentiment = Field(default=Sentiment.NEUTRAL)
    key_events: list[str] = Field(default_factory=list)
    geopolitical_risks: list[str] = Field(default_factory=list)
    economic_indicators: dict[str, float] = Field(default_factory=dict)
    news_sentiment: Optional[float] = None


class FinBERTSentimentReport(AgentReport):
    """Report from FinBERT Sentiment Analyst."""

    agent_role: AgentRole = Field(default=AgentRole.FINBERT_SENTIMENT_ANALYST)
    sentiment: Sentiment = Field(default=Sentiment.NEUTRAL)
    sentiment_score: float = Field(default=0.0, ge=-1.0, le=1.0)
    positive_score: float = Field(default=0.0, ge=0.0, le=1.0)
    negative_score: float = Field(default=0.0, ge=0.0, le=1.0)
    neutral_score: float = Field(default=0.0, ge=0.0, le=1.0)
    text_analyzed: list[str] = Field(default_factory=list)


class FinGPTGenerativeReport(AgentReport):
    """Report from FinGPT Generative Analyst."""

    agent_role: AgentRole = Field(default=AgentRole.FINGPT_GENERATIVE_ANALYST)
    analysis_type: str = Field(default="general")
    key_insights: list[str] = Field(default_factory=list)
    risks_identified: list[str] = Field(default_factory=list)
    opportunities_identified: list[str] = Field(default_factory=list)
    detailed_summary: str = Field(default="")


# (rest of file unchanged)