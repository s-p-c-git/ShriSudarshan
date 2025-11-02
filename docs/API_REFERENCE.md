# API Reference - Project Shri Sudarshan

## Overview

This document provides a comprehensive reference for the data schemas, providers, and agent interfaces in Project Shri Sudarshan.

## Table of Contents

- [Data Schemas](#data-schemas)
  - [Enums](#enums)
  - [Agent Reports](#agent-reports)
  - [Strategy and Execution](#strategy-and-execution)
  - [Oversight](#oversight)
  - [Learning](#learning)
- [Data Providers](#data-providers)
  - [MarketDataProvider](#marketdataprovider)
  - [NewsProvider](#newsprovider)
- [Agent Base Classes](#agent-base-classes)

---

## Data Schemas

All data schemas are defined in `src/data/schemas.py` using Pydantic for validation.

### Enums

#### AgentRole

Defines the role of each agent in the system.

```python
class AgentRole(str, Enum):
    # Market Intelligence Team
    FUNDAMENTALS_ANALYST = "fundamentals_analyst"
    MACRO_NEWS_ANALYST = "macro_news_analyst"
    SENTIMENT_ANALYST = "sentiment_analyst"
    TECHNICAL_ANALYST = "technical_analyst"
    
    # Strategy & Research Team
    BULLISH_RESEARCHER = "bullish_researcher"
    BEARISH_RESEARCHER = "bearish_researcher"
    DERIVATIVES_STRATEGIST = "derivatives_strategist"
    
    # Execution Team
    EQUITY_TRADER = "equity_trader"
    FNO_TRADER = "fno_trader"
    
    # Oversight & Learning Team
    PORTFOLIO_MANAGER = "portfolio_manager"
    RISK_MANAGER = "risk_manager"
    REFLECTIVE_AGENT = "reflective_agent"
```

**Total Agents**: 11

#### Sentiment

Represents sentiment levels for analysis.

```python
class Sentiment(str, Enum):
    VERY_BULLISH = "very_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    VERY_BEARISH = "very_bearish"
```

#### TrendDirection

Represents technical trend direction.

```python
class TrendDirection(str, Enum):
    STRONG_UPTREND = "strong_uptrend"
    UPTREND = "uptrend"
    SIDEWAYS = "sideways"
    DOWNTREND = "downtrend"
    STRONG_DOWNTREND = "strong_downtrend"
```

#### StrategyType

Defines supported trading strategies.

```python
class StrategyType(str, Enum):
    LONG_EQUITY = "long_equity"
    SHORT_EQUITY = "short_equity"
    COVERED_CALL = "covered_call"
    PROTECTIVE_PUT = "protective_put"
    BULL_CALL_SPREAD = "bull_call_spread"
    BEAR_PUT_SPREAD = "bear_put_spread"
    IRON_CONDOR = "iron_condor"
    STRADDLE = "straddle"
    STRANGLE = "strangle"
    CALENDAR_SPREAD = "calendar_spread"
```

**Total Strategies**: 10

#### TradeDirection

```python
class TradeDirection(str, Enum):
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"
```

#### OrderType

```python
class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
```

#### OrderSide

```python
class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"
```

---

### Agent Reports

#### AgentReport (Base Class)

Base class for all agent reports.

**Fields**:
- `symbol: str` - Stock symbol
- `summary: str` - Brief summary (optional, default="")
- `confidence: float` - Confidence level (0.0 to 1.0, default=0.5)
- `agent_role: AgentRole` - Role of the agent
- `timestamp: datetime` - Report timestamp (auto-generated)
- `metadata: Dict[str, Any]` - Additional metadata (optional)

#### FundamentalsReport

Report from the Fundamentals Analyst.

**Inherits**: AgentReport

**Core Fields**:
- `analysis: str` - Detailed analysis text
- `key_points: List[str]` - Key analysis points
- `confidence_level: int` - Confidence on 1-10 scale
- `intrinsic_value: Optional[float]` - Estimated intrinsic value
- `investment_thesis: Sentiment` - Overall thesis
- `risk_factors: List[str]` - Identified risks

**Financial Metrics** (all Optional[float]):
- `revenue`, `net_income`, `eps`
- `pe_ratio`, `forward_pe`, `peg_ratio`
- `price_to_book`, `price_to_sales`
- `profit_margin`, `operating_margin`
- `return_on_equity`, `return_on_assets`
- `revenue_growth`, `earnings_growth`
- `debt_to_equity`, `current_ratio`, `quick_ratio`
- `free_cash_flow`, `dividend_yield`, `payout_ratio`

**Additional**:
- `financial_metrics: Dict[str, Any]` - Raw metrics dictionary

#### MacroNewsReport

Report from the Macro & News Analyst.

**Inherits**: AgentReport

**Core Fields**:
- `analysis: str` - Detailed analysis
- `key_points: List[str]` - Key points
- `confidence_level: int` - 1-10 confidence

**Analysis Fields**:
- `market_sentiment: Sentiment` - Overall market sentiment
- `key_events: List[str]` - Important events
- `economic_indicators: Dict[str, Any]` - Economic data
- `geopolitical_risks: List[str]` - Risk factors
- `central_bank_outlook: Optional[str]` - Fed/central bank view
- `sector_trends: List[str]` - Sector-level trends

**Agent-Specific**:
- `macro_themes: List[str]` - Major themes
- `news_items: List[str]` - Key news
- `risk_events: List[str]` - Risk events

#### SentimentReport

Report from the Sentiment Analyst.

**Inherits**: AgentReport

**Core Fields**:
- `analysis: str` - Analysis text
- `key_points: List[str]` - Key points
- `confidence_level: int` - 1-10 confidence

**Sentiment Fields**:
- `social_sentiment: Sentiment` - Social media sentiment
- `sentiment_score: float` - Score from -1.0 to 1.0
- `sentiment_trend: Optional[str]` - Trend description
- `retail_interest: Optional[str]` - Retail activity
- `institutional_activity: Optional[str]` - Institutional activity
- `news_sentiment: Optional[Sentiment]` - News-based sentiment
- `mentions_count: Optional[int]` - Social mentions
- `sentiment_volatility: Optional[float]` - Volatility measure

**Agent-Specific**:
- `trending_topics: List[str]` - Trending topics
- `retail_positioning: Optional[str]` - Retail position

#### TechnicalReport

Report from the Technical Analyst.

**Inherits**: AgentReport

**Core Fields**:
- `analysis: str` - Analysis text
- `key_points: List[str]` - Key points
- `confidence_level: int` - 1-10 confidence

**Technical Fields**:
- `trend_direction: TrendDirection` - Overall trend
- `support_levels: List[float]` - Support price levels
- `resistance_levels: List[float]` - Resistance price levels
- `indicators: Dict[str, Any]` - Technical indicators
- `chart_patterns: List[str]` - Identified patterns
- `volume_analysis: Optional[str]` - Volume insights
- `momentum_signals: List[str]` - Momentum indicators

**Specific Indicators** (Optional):
- `moving_averages: Dict[str, float]` - MA values
- `rsi: Optional[float]` - RSI value
- `macd: Optional[Dict[str, float]]` - MACD values
- `bollinger_bands: Optional[Dict[str, float]]` - BB values

---

### Strategy and Execution

#### DebateArgument

Represents an argument in the bull/bear debate.

**Fields**:
- `agent_role: AgentRole` - Role making the argument
- `round_number: int` - Debate round (>=1)
- `argument: str` - The argument text
- `supporting_evidence: List[str]` - Evidence points
- `counterpoints: List[str]` - Counterarguments
- `confidence: float` - Confidence (0.0 to 1.0)
- `timestamp: datetime` - Auto-generated

#### StrategyProposal

Trading strategy proposal from the Derivatives Strategist.

**Required Fields**:
- `symbol: str` - Target symbol
- `strategy_type: StrategyType` - Strategy to use
- `direction: TradeDirection` - Trade direction
- `rationale: str` - Strategy rationale
- `expected_return: float` - Expected return in %
- `max_loss: float` - Max potential loss in %
- `holding_period: str` - Expected duration

**Optional Fields**:
- `entry_criteria: List[str]` - Entry conditions
- `exit_criteria: List[str]` - Exit conditions
- `risk_factors: List[str]` - Risk factors
- `market_conditions: Optional[str]` - Market view
- `volatility_analysis: Optional[Dict[str, Any]]` - Vol analysis
- `greeks: Optional[Dict[str, float]]` - Options greeks
- `confidence: float` - Confidence (0.0 to 1.0)
- `timestamp: datetime` - Auto-generated

#### Order

Individual order specification.

**Required Fields**:
- `symbol: str` - Symbol
- `side: OrderSide` - BUY or SELL
- `quantity: int` - Quantity (>0)
- `order_type: OrderType` - Order type

**Optional Fields**:
- `price: Optional[float]` - Limit price
- `stop_price: Optional[float]` - Stop price
- `expiry: Optional[str]` - Options expiry (YYYY-MM-DD)
- `strike: Optional[float]` - Strike price
- `option_type: Optional[str]` - "call" or "put"
- `time_in_force: str` - Default "DAY"
- `notes: Optional[str]` - Order notes

#### ExecutionPlan

Execution plan from trader agents.

**Required Fields**:
- `symbol: str` - Symbol
- `strategy_type: StrategyType` - Strategy
- `orders: List[Order]` - List of orders
- `estimated_cost: float` - Total cost
- `estimated_slippage: float` - Expected slippage
- `estimated_commissions: float` - Commission estimate

**Optional Fields**:
- `execution_strategy: Optional[str]` - Execution approach
- `timing_recommendations: Optional[str]` - Timing notes
- `risk_mitigation: List[str]` - Risk controls
- `notes: Optional[str]` - Additional notes
- `timestamp: datetime` - Auto-generated

---

### Oversight

#### RiskAssessment

Risk assessment from the Risk Manager.

**Required Fields**:
- `symbol: str` - Symbol
- `approved: bool` - Approval status
- `var_estimate: float` - Value at Risk
- `position_size_pct: float` - Position size as % of portfolio
- `recommendation: str` - Risk recommendation

**Optional Fields**:
- `portfolio_impact: Optional[float]` - Portfolio impact
- `correlation_risk: Optional[float]` - Correlation measure
- `sector_concentration: Optional[float]` - Sector %
- `max_drawdown_estimate: Optional[float]` - Max DD estimate
- `risk_warnings: List[str]` - Warning messages
- `conditions: List[str]` - Approval conditions
- `timestamp: datetime` - Auto-generated

#### PortfolioDecision

Final decision from the Portfolio Manager.

**Required Fields**:
- `symbol: str` - Symbol
- `approved: bool` - Final approval
- `decision_rationale: str` - Decision reasoning
- `position_size: float` - Approved position size

**Optional Fields**:
- `strategic_fit: Optional[str]` - Strategy alignment
- `opportunity_cost: Optional[float]` - Alt opportunity cost
- `portfolio_allocation: Optional[Dict[str, float]]` - Allocation map
- `monitoring_requirements: List[str]` - Monitoring needs
- `conditions: List[str]` - Conditions
- `review_date: Optional[datetime]` - Review date
- `timestamp: datetime` - Auto-generated

---

### Learning

#### TradeOutcome

Record of trade outcome for learning.

**Required Fields**:
- `trade_id: str` - Unique trade ID
- `symbol: str` - Symbol
- `strategy_type: StrategyType` - Strategy used
- `entry_date: datetime` - Entry timestamp
- `entry_price: float` - Entry price
- `quantity: int` - Position size

**Optional Fields**:
- `exit_date: Optional[datetime]` - Exit timestamp
- `exit_price: Optional[float]` - Exit price
- `realized_pnl: Optional[float]` - P&L
- `return_pct: Optional[float]` - Return %
- `outcome: str` - "pending", "win", "loss", "breakeven"
- `trade_notes: Optional[str]` - Notes
- `market_conditions: Optional[Dict[str, Any]]` - Market state
- `original_strategy: Optional[Dict[str, Any]]` - Original plan
- `original_rationale: Optional[str]` - Original reasoning
- `timestamp: datetime` - Auto-generated

#### Reflection

Reflection on trade outcome from the Reflective Agent.

**Required Fields**:
- `trade_id: str` - Trade ID
- `symbol: str` - Symbol

**Learning Fields**:
- `outcome_summary: Optional[str]` - Outcome summary
- `what_worked: List[str]` - What worked well
- `what_failed: List[str]` - What failed
- `market_lessons: List[str]` - Market insights
- `strategic_adjustments: List[str]` - Recommended adjustments
- `confidence_impact: Optional[str]` - Confidence adjustment
- `conceptual_recommendations: Optional[str]` - System improvements

**Compatibility Fields**:
- `analysis_summary: str` - Summary text (optional)
- `lessons_learned: List[str]` - General lessons
- `strategic_recommendations: List[str]` - Strategy recommendations

**Metrics**:
- `confidence_accuracy: Optional[float]` - How accurate was confidence?
- `prediction_quality: Optional[str]` - Quality assessment
- `timestamp: datetime` - Auto-generated

---

## Data Providers

### MarketDataProvider

Located in `src/data/providers/market_data.py`.

Provides market data using yfinance.

#### Methods

##### `get_price_history(symbol, period, interval, start, end)`

Get historical OHLCV data.

**Parameters**:
- `symbol: str` - Stock symbol
- `period: str` - Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
- `interval: str` - Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
- `start: Optional[str]` - Start date (YYYY-MM-DD)
- `end: Optional[str]` - End date (YYYY-MM-DD)

**Returns**: `pd.DataFrame` with OHLCV data

##### `get_current_price(symbol)`

Get current price.

**Returns**: `Optional[float]` - Current price or None

##### `get_info(symbol)`

Get general company information.

**Returns**: `Dict[str, Any]` - Company info

##### `get_fundamentals(symbol)`

Get comprehensive fundamental metrics.

**Returns**: `Dict[str, Any]` - 30+ fundamental metrics

##### `get_financial_statements(symbol)`

Get financial statements.

**Returns**: `Dict[str, pd.DataFrame]` - Income statement, balance sheet, cash flow (annual and quarterly)

##### `get_options_chain(symbol, expiry_date)`

Get options chain data.

**Returns**: `Dict[str, Any]` - Calls, puts, expiry dates

##### `get_available_expiries(symbol)`

Get available option expiry dates.

**Returns**: `List[str]` - List of expiry dates

##### `calculate_technical_indicators(symbol)`

Calculate technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, etc.).

**Returns**: `Dict[str, Any]` - Technical indicators

##### `get_market_overview()`

Get overview of major market indices.

**Returns**: `Dict[str, Any]` - Index prices and changes

### NewsProvider

Located in `src/data/providers/news.py`.

Provides news aggregation and sentiment analysis.

#### Methods

##### `get_company_news(symbol, days_back, max_articles)`

Get company-specific news articles.

**Parameters**:
- `symbol: str` - Stock symbol
- `days_back: int` - Days to look back (default=7)
- `max_articles: int` - Max articles (default=20)

**Returns**: `List[Dict[str, Any]]` - News articles with sentiment

##### `get_market_news(days_back, max_articles)`

Get general market news.

**Returns**: `List[Dict[str, Any]]` - Market news articles

##### `aggregate_sentiment(symbol, days_back)`

Aggregate sentiment from multiple news sources.

**Returns**: `Dict[str, Any]` - Sentiment score, label, counts, recent headlines

##### `get_economic_calendar(days_ahead)`

Get upcoming economic events (placeholder).

**Returns**: `List[Dict[str, Any]]` - Economic events

---

## Agent Base Classes

Located in `src/agents/base.py`.

### BaseAgent

Abstract base class for all agents.

**Constructor Parameters**:
- `role: AgentRole` - Agent's role
- `system_prompt: str` - System prompt
- `model_name: Optional[str]` - LLM model (default: settings.standard_model)
- `temperature: float` - Generation temperature (default: 0.7)

**Abstract Methods**:
- `async def analyze(context: Dict[str, Any]) -> AgentReport` - Must be implemented

**Helper Methods**:
- `async def _generate_response(input_text: str) -> str` - Generate LLM response
- `def get_metadata() -> Dict[str, Any]` - Get agent metadata

### CriticalAgent

Base class for critical decision-making agents. Uses premium model (GPT-4o) by default.

**Inherits**: BaseAgent

**Constructor Parameters**:
- `role: AgentRole` - Agent's role
- `system_prompt: str` - System prompt
- `temperature: float` - Generation temperature (default: 0.7)

**Agents Using CriticalAgent**:
- Portfolio Manager
- Risk Manager
- Derivatives Strategist
- Reflective Agent

---

## Usage Examples

### Creating a Report

```python
from src.data.schemas import FundamentalsReport, Sentiment

report = FundamentalsReport(
    symbol="AAPL",
    analysis="Strong fundamentals with solid earnings growth",
    key_points=["Revenue up 15%", "High profit margins", "Strong cash position"],
    confidence_level=8,
    investment_thesis=Sentiment.BULLISH,
    pe_ratio=28.5,
    revenue_growth=0.15,
    debt_to_equity=1.2,
)
```

### Using MarketDataProvider

```python
from src.data.providers import MarketDataProvider

provider = MarketDataProvider()

# Get price history
history = provider.get_price_history("AAPL", period="1mo", interval="1d")

# Get fundamentals
fundamentals = provider.get_fundamentals("AAPL")

# Calculate technical indicators
indicators = provider.calculate_technical_indicators("AAPL")
```

### Using NewsProvider

```python
from src.data.providers import NewsProvider

provider = NewsProvider()

# Get company news
news = provider.get_company_news("AAPL", days_back=7, max_articles=20)

# Get aggregate sentiment
sentiment = provider.aggregate_sentiment("AAPL", days_back=7)
print(f"Sentiment: {sentiment['sentiment_label']} ({sentiment['sentiment_score']:.2f})")
```

---

## Validation

All schemas use Pydantic validation:
- **Type checking**: Automatic type validation
- **Range validation**: `confidence` (0.0-1.0), `confidence_level` (1-10), `sentiment_score` (-1.0 to 1.0)
- **Required fields**: Enforced at instantiation
- **Default values**: Provided for optional fields

---

## Error Handling

Data providers implement graceful error handling:
- Return empty DataFrames/dicts on errors
- Log errors with context
- Never raise unhandled exceptions
- Provide sensible defaults

---

## See Also

- [Architecture Documentation](architecture.md)
- [Getting Started Guide](getting_started.md)
- [Testing Guide](TESTING.md)
