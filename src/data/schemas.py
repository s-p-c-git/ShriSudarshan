"""
Data schemas for Project Shri Sudarshan.

This module defines all Pydantic models and enums used throughout the system.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..utils.logger import get_logger


logger = get_logger(__name__)


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

    @model_validator(mode="before")
    @classmethod
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
            except (ValueError, TypeError) as e:
                logger.warning(
                    "Failed to convert confidence_level to confidence",
                    error=str(e),
                    raw_value=values.get("confidence_level"),
                )
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


# =============================================================================
# Core Debate, Strategy, Execution, and Oversight Models
# =============================================================================


class DebateArgument(BaseModel):
    """
    Represents a structured argument in the debate phase.

    Args:
        round_number: The debate round number.
        role: Role of the agent making the argument.
        position: Bullish or bearish position.
        argument: Textual argument content.
        supporting_evidence: List of supporting facts or data.
        counterpoints: List of counterpoints to opposing arguments.
        confidence: Confidence score (0.0 - 1.0), optional.
        timestamp: Timestamp when argument was created (auto-generated).
    """

    agent_role: AgentRole
    stance: Sentiment
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_evidence: list[str] = Field(default_factory=list)
    counterpoints: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)


class StrategyProposal(BaseModel):
    """
    Represents a proposed trading strategy (equity or derivatives).

    Args:
        symbol: Target security symbol.
        strategy_type: Type of strategy (e.g., 'option_spread', 'long_equity').
        direction: Trade direction (long/short/neutral).
        rationale: Rationale for the proposal.
        expected_return: Estimated return (percentage).
        max_loss: Maximum acceptable loss (percentage).
        entry_conditions: Conditions that should be met to enter the trade.
        exit_conditions: Conditions for exiting the trade.
        position_size_pct: Position size as percentage of portfolio.
        time_horizon_days: Expected holding period in days.
        confidence_score: Confidence in the strategy (0.0 - 1.0).
        debate_summary: Summary of debate leading to this strategy.
        agent_role: Role of the proposing agent (optional for backwards compatibility).
        details: Structured details of the strategy (for backwards compatibility).
        risk_level: Qualitative risk level (for backwards compatibility).
        holding_period: Legacy field (superseded by time_horizon_days).
        risk_factors: List of identified risk factors.
        timestamp: Creation timestamp.
    """

    strategy_type: str
    symbol: str
    strategy_type: str
    direction: TradeDirection
    rationale: str
    expected_return: float
    max_loss: float
    
    # Fields with defaults (support both old and new names via aliases)
    entry_conditions: list[str] = Field(default_factory=list, alias="entry_criteria")
    exit_conditions: list[str] = Field(default_factory=list, alias="exit_criteria")
    position_size_pct: float = 0.02  # Default 2% position size
    time_horizon_days: int = 30  # Default 30 days
    confidence_score: float = Field(default=0.5, ge=0.0, le=1.0, alias="confidence")
    debate_summary: str = ""
    
    # Optional fields for backwards compatibility
    agent_role: Optional[AgentRole] = None
    details: dict[str, Any] = Field(default_factory=dict)
    risk_level: Optional[str] = None
    holding_period: Optional[str] = None
    risk_factors: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class Order(BaseModel):
    """
    Represents a single trade order.

    Args:
        symbol: Security symbol.
        side: Order side (BUY or SELL).
        order_type: Order type (MARKET, LIMIT, STOP, STOP_LIMIT).
        quantity: Number of shares/contracts (must be positive).
        limit_price: Limit price for LIMIT and STOP_LIMIT orders.
        stop_price: Stop price for STOP and STOP_LIMIT orders.
        time_in_force: Time in force (DAY, GTC, IOC, FOK).
        timestamp: Time of order creation.
    """

    symbol: str
    order_type: str
    quantity: float
    price: Optional[float] = None
    order_style: str = "market"
    timestamp: datetime = Field(default_factory=datetime.now)


class ExecutionPlan(BaseModel):
    """
    Represents a plan for executing one or more orders.

    Args:
        agent_role: Role of the executing agent.
        orders: List of orders to execute.
        execution_strategy: Description of execution approach.
        notes: Additional notes.
    """

    agent_role: AgentRole
    orders: list[Order] = Field(default_factory=list)
    execution_strategy: Optional[str] = None
    notes: Optional[str] = None


class RiskAssessment(BaseModel):
    """
    Represents a risk manager's assessment of a proposed strategy.

    Args:
        agent_role: Role of the risk manager.
        risk_score: Quantitative risk score (0.0 - 1.0).
        risk_factors: List of identified risk factors.
        risk_mitigation: Suggested mitigations.
        approved: Whether the risk is acceptable.
        comments: Additional comments.
    """

    agent_role: AgentRole
    risk_score: float = Field(ge=0.0, le=1.0)
    risk_factors: list[str] = Field(default_factory=list)
    risk_mitigation: Optional[str] = None
    approved: bool = False
    comments: Optional[str] = None


class PortfolioDecision(BaseModel):
    """
    Represents the portfolio manager's final decision.

    Args:
        agent_role: Role of the portfolio manager.
        approved: Whether the strategy is approved.
        rationale: Rationale for the decision.
        modifications: Any modifications to the proposal.
    """

    agent_role: AgentRole
    approved: bool
    rationale: Optional[str] = None
    modifications: Optional[dict[str, Any]] = None


class TradeOutcome(BaseModel):
    """
    Represents the outcome of an executed trade.

    Args:
        symbol: Security symbol.
        entry_price: Price at entry.
        exit_price: Price at exit.
        quantity: Number of shares/contracts.
        pnl: Profit or loss.
        timestamp: Time of trade completion.
    """

    symbol: str
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    timestamp: datetime = Field(default_factory=datetime.now)


class Reflection(BaseModel):
    """
    Represents post-trade reflection and learning.

    Args:
        agent_role: Role of the reflective agent.
        trade_outcome: Outcome of the trade.
        lessons_learned: Key lessons.
        improvement_suggestions: Suggestions for future improvement.
    """

    agent_role: AgentRole
    trade_outcome: TradeOutcome
    lessons_learned: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)
