"""
Data schemas for Project Shri Sudarshan.

This module defines all Pydantic models and enums used throughout the system.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


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


# =============================================================================
# Strategy & Research Models
# =============================================================================


class DebateArgument(BaseModel):
    """Argument presented in bull/bear debate."""

    model_config = ConfigDict(use_enum_values=True)

    agent_role: AgentRole
    round_number: int
    argument: str
    supporting_evidence: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)


class StrategyProposal(BaseModel):
    """Strategy proposal from Derivatives Strategist."""

    model_config = ConfigDict(use_enum_values=True)

    symbol: str
    strategy_type: StrategyType
    direction: TradeDirection
    rationale: str
    expected_return: float
    max_loss: float
    holding_period: str
    entry_criteria: list[str] = Field(default_factory=list)
    exit_criteria: list[str] = Field(default_factory=list)
    risk_factors: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)


# =============================================================================
# Execution Models
# =============================================================================


class Order(BaseModel):
    """Order details for execution."""

    model_config = ConfigDict(use_enum_values=True)

    symbol: str
    side: OrderSide
    quantity: int = Field(gt=0)
    order_type: OrderType
    price: Optional[float] = None
    stop_price: Optional[float] = None
    # Options-specific fields
    expiry: Optional[str] = None
    strike: Optional[float] = None
    option_type: Optional[str] = None  # "call" or "put"


class ExecutionPlan(BaseModel):
    """Execution plan from Trader agents."""

    model_config = ConfigDict(use_enum_values=True)

    symbol: str
    strategy_type: StrategyType
    orders: list[Order]
    estimated_cost: float
    estimated_slippage: float = Field(default=0.0)
    timing_recommendation: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# =============================================================================
# Oversight Models
# =============================================================================


class RiskAssessment(BaseModel):
    """Risk assessment from Risk Manager."""

    symbol: str
    approved: bool
    var_estimate: float
    position_size_pct: float
    sector_exposure: Optional[str] = None
    risk_warnings: list[str] = Field(default_factory=list)
    recommendation: str
    timestamp: datetime = Field(default_factory=datetime.now)


class PortfolioDecision(BaseModel):
    """Final decision from Portfolio Manager."""

    symbol: str
    approved: bool
    decision_rationale: str
    position_size: float
    monitoring_requirements: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


# =============================================================================
# Learning & Reflection Models
# =============================================================================


class TradeOutcome(BaseModel):
    """Record of trade outcome for learning."""

    model_config = ConfigDict(use_enum_values=True)

    trade_id: str
    symbol: str
    strategy_type: StrategyType
    entry_date: datetime
    exit_date: Optional[datetime] = None
    entry_price: float
    exit_price: Optional[float] = None
    quantity: int
    realized_pnl: Optional[float] = None
    return_pct: Optional[float] = None
    outcome: str = Field(default="pending")  # "win", "loss", "breakeven", "pending"
    notes: Optional[str] = None


class Reflection(BaseModel):
    """Reflection on trade outcomes for continuous learning."""

    trade_id: str
    symbol: str
    analysis_summary: str
    what_worked: list[str] = Field(default_factory=list)
    what_failed: list[str] = Field(default_factory=list)
    lessons_learned: list[str] = Field(default_factory=list)
    strategic_recommendations: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
