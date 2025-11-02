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

### Complete Workflow Example

```python
"""
Complete example: Running a full trading workflow programmatically.
"""
import asyncio
from src.orchestration import TradingWorkflow
from src.utils import setup_logging, get_logger

async def run_complete_workflow():
    """Execute complete trading workflow for a symbol."""
    # Setup
    setup_logging()
    logger = get_logger(__name__)
    
    # Create workflow
    workflow = TradingWorkflow()
    
    # Run analysis
    symbol = "AAPL"
    logger.info(f"Starting workflow for {symbol}")
    
    result = await workflow.run(symbol=symbol)
    
    # Access results
    print(f"\n{'='*60}")
    print(f"Workflow Results for {symbol}")
    print(f"{'='*60}\n")
    
    # Market Intelligence Results
    if result.get('analyst_reports'):
        print("Market Intelligence Analysis:")
        for role, report in result['analyst_reports'].items():
            print(f"  {role}: Confidence {report.confidence_level}/10")
    
    # Debate Results
    if result.get('debate_arguments'):
        print(f"\nDebate Rounds: {len(result['debate_arguments'])}")
        print(f"Debate Outcome: {result.get('debate_outcome', 'N/A')}")
    
    # Strategy Results
    if result.get('strategy_proposal'):
        strategy = result['strategy_proposal']
        print(f"\nProposed Strategy: {strategy.strategy_type}")
        print(f"Expected Return: {strategy.expected_return}%")
        print(f"Max Loss: {strategy.max_loss}%")
    
    # Risk Assessment
    if result.get('risk_assessment'):
        risk = result['risk_assessment']
        print(f"\nRisk Assessment: {'Approved' if risk.approved else 'Rejected'}")
        print(f"VaR Estimate: {risk.var_estimate:.2%}")
    
    # Final Decision
    if result.get('portfolio_decision'):
        decision = result['portfolio_decision']
        print(f"\nFinal Decision: {'Approved' if decision.approved else 'Rejected'}")
        if decision.approved:
            print(f"Position Size: {decision.position_size}% of portfolio")
    
    print(f"\n{'='*60}\n")
    
    return result

if __name__ == "__main__":
    result = asyncio.run(run_complete_workflow())
```

### Using Individual Agents

```python
"""
Example: Using individual agents for custom analysis.
"""
import asyncio
from src.agents.market_intelligence import (
    FundamentalsAnalyst,
    TechnicalAnalyst,
    SentimentAnalyst,
    MacroNewsAnalyst
)
from src.data.providers import MarketDataProvider, NewsProvider

async def custom_analysis(symbol: str):
    """Run custom multi-agent analysis."""
    # Setup data providers
    market_data = MarketDataProvider()
    news_provider = NewsProvider()
    
    # Create agents
    fundamentals = FundamentalsAnalyst()
    technical = TechnicalAnalyst()
    sentiment = SentimentAnalyst()
    macro_news = MacroNewsAnalyst()
    
    # Prepare context
    context = {
        "symbol": symbol,
        "market_data_provider": market_data,
        "news_provider": news_provider
    }
    
    # Run analyses concurrently
    results = await asyncio.gather(
        fundamentals.analyze(context),
        technical.analyze(context),
        sentiment.analyze(context),
        macro_news.analyze(context),
        return_exceptions=True
    )
    
    # Process results
    fundamental_report, technical_report, sentiment_report, news_report = results
    
    # Aggregate confidence
    avg_confidence = sum([
        r.confidence_level for r in results if hasattr(r, 'confidence_level')
    ]) / 4
    
    print(f"\nAnalysis for {symbol}")
    print(f"Average Confidence: {avg_confidence:.1f}/10")
    print(f"\nFundamentals: {fundamental_report.investment_thesis}")
    print(f"Technical: {technical_report.trend_direction}")
    print(f"Sentiment: {sentiment_report.social_sentiment}")
    print(f"Macro: {news_report.market_sentiment}")
    
    return {
        "fundamentals": fundamental_report,
        "technical": technical_report,
        "sentiment": sentiment_report,
        "macro_news": news_report,
        "avg_confidence": avg_confidence
    }

# Usage
symbol = "AAPL"
analysis = asyncio.run(custom_analysis(symbol))
```

### Working with Data Providers

```python
"""
Example: Advanced usage of MarketDataProvider.
"""
from src.data.providers import MarketDataProvider
from datetime import datetime, timedelta
import pandas as pd

def analyze_stock_deeply(symbol: str):
    """Perform deep analysis using MarketDataProvider."""
    provider = MarketDataProvider()
    
    # 1. Get price history
    print(f"Analyzing {symbol}...")
    history = provider.get_price_history(symbol, period="6mo", interval="1d")
    
    if history.empty:
        print(f"No data available for {symbol}")
        return None
    
    # 2. Current price and basic info
    current_price = provider.get_current_price(symbol)
    info = provider.get_info(symbol)
    
    print(f"Current Price: ${current_price:.2f}")
    print(f"Company: {info.get('longName', 'N/A')}")
    print(f"Sector: {info.get('sector', 'N/A')}")
    
    # 3. Fundamental metrics
    fundamentals = provider.get_fundamentals(symbol)
    
    print("\nValuation Metrics:")
    print(f"  P/E Ratio: {fundamentals.get('trailing_pe', 'N/A')}")
    print(f"  PEG Ratio: {fundamentals.get('peg_ratio', 'N/A')}")
    print(f"  Debt/Equity: {fundamentals.get('debt_to_equity', 'N/A')}")
    
    # 4. Technical indicators
    indicators = provider.calculate_technical_indicators(symbol)
    
    print("\nTechnical Indicators:")
    print(f"  RSI: {indicators.get('rsi', 'N/A')}")
    print(f"  MACD: {indicators.get('macd', {}).get('macd', 'N/A')}")
    print(f"  SMA 50: ${indicators.get('sma_50', 'N/A')}")
    print(f"  SMA 200: ${indicators.get('sma_200', 'N/A')}")
    
    # 5. Support and resistance
    support_levels = indicators.get('support_levels', [])
    resistance_levels = indicators.get('resistance_levels', [])
    
    print("\nKey Levels:")
    print(f"  Support: {support_levels}")
    print(f"  Resistance: {resistance_levels}")
    
    # 6. Options data (if available)
    try:
        expiries = provider.get_available_expiries(symbol)
        if expiries:
            print(f"\nOptions Expiries: {len(expiries)} available")
            
            # Get nearest expiry options chain
            options = provider.get_options_chain(symbol, expiry_date=expiries[0])
            
            print(f"Calls: {len(options['calls'])} strikes")
            print(f"Puts: {len(options['puts'])} strikes")
    except:
        print("\nOptions data not available")
    
    # 7. Financial statements
    statements = provider.get_financial_statements(symbol)
    
    if statements.get('income_statement') is not None:
        print("\nFinancial Statements Available:")
        print(f"  Income Statement: {statements['income_statement'].shape}")
        print(f"  Balance Sheet: {statements['balance_sheet'].shape}")
        print(f"  Cash Flow: {statements['cash_flow'].shape}")
    
    return {
        "price": current_price,
        "history": history,
        "fundamentals": fundamentals,
        "indicators": indicators,
        "info": info
    }

# Usage
data = analyze_stock_deeply("AAPL")
```

### Working with News and Sentiment

```python
"""
Example: Sentiment analysis using NewsProvider.
"""
from src.data.providers import NewsProvider
from datetime import datetime

def analyze_sentiment_trends(symbol: str, days: int = 30):
    """Analyze sentiment trends over time."""
    provider = NewsProvider()
    
    print(f"Analyzing sentiment for {symbol} over {days} days...")
    
    # Get news articles
    news = provider.get_company_news(symbol, days_back=days, max_articles=50)
    
    if not news:
        print("No news found")
        return None
    
    print(f"Found {len(news)} articles")
    
    # Aggregate sentiment
    sentiment_data = provider.aggregate_sentiment(symbol, days_back=days)
    
    print(f"\nOverall Sentiment:")
    print(f"  Score: {sentiment_data['sentiment_score']:.2f} (-1 to +1)")
    print(f"  Label: {sentiment_data['sentiment_label']}")
    print(f"  Positive Articles: {sentiment_data.get('positive_count', 0)}")
    print(f"  Negative Articles: {sentiment_data.get('negative_count', 0)}")
    print(f"  Neutral Articles: {sentiment_data.get('neutral_count', 0)}")
    
    print(f"\nRecent Headlines:")
    for headline in sentiment_data.get('recent_headlines', [])[:5]:
        print(f"  - {headline}")
    
    # Analyze individual articles
    print(f"\nDetailed Article Analysis:")
    for article in news[:5]:
        print(f"\nTitle: {article['title']}")
        print(f"Date: {article['published']}")
        print(f"Sentiment: {article.get('sentiment', 'N/A')}")
        print(f"URL: {article['link']}")
    
    return {
        "news_articles": news,
        "aggregate_sentiment": sentiment_data
    }

# Usage
sentiment_analysis = analyze_sentiment_trends("TSLA", days=7)
```

### Creating Custom Strategies

```python
"""
Example: Creating custom strategy proposals.
"""
from src.data.schemas import (
    StrategyProposal,
    StrategyType,
    TradeDirection,
    Order,
    OrderSide,
    OrderType
)
from datetime import datetime, timedelta

def create_bull_call_spread(symbol: str, current_price: float):
    """Create a bull call spread strategy."""
    
    # Define strategy parameters
    lower_strike = round(current_price * 0.98, 2)  # 2% OTM
    upper_strike = round(current_price * 1.05, 2)  # 5% OTM
    expiry_date = (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
    
    # Create strategy proposal
    strategy = StrategyProposal(
        symbol=symbol,
        strategy_type=StrategyType.BULL_CALL_SPREAD,
        direction=TradeDirection.LONG,
        rationale=f"""
        Bull call spread on {symbol} with current price ${current_price:.2f}.
        
        Buy {lower_strike} call and sell {upper_strike} call for 45 DTE.
        
        Rationale:
        - Moderately bullish outlook
        - Defined risk and reward
        - Lower cost than outright call purchase
        - Benefits from upside to {upper_strike}
        """,
        expected_return=15.0,  # 15% return on capital
        max_loss=5.0,  # 5% max loss
        holding_period="30-45 days",
        entry_criteria=[
            f"Price between ${lower_strike} and ${current_price}",
            "Implied volatility below 30th percentile",
            "No major earnings in next 45 days"
        ],
        exit_criteria=[
            "Take profit at 50% of max gain",
            "Stop loss at 50% of max loss",
            "Close at 21 DTE regardless of P&L"
        ],
        risk_factors=[
            "Stock could move above upper strike (capped gains)",
            "Time decay accelerates near expiration",
            "Requires stock to move up to be profitable"
        ],
        greeks={
            "delta": 0.40,
            "gamma": 0.05,
            "theta": -0.10,
            "vega": 0.20
        },
        volatility_analysis={
            "iv": 0.22,
            "hv": 0.25,
            "iv_percentile": 25,
            "analysis": "IV relatively low, good time to buy options"
        },
        confidence=7.5
    )
    
    return strategy

# Usage
strategy = create_bull_call_spread("AAPL", 180.50)
print(f"Strategy: {strategy.strategy_type}")
print(f"Expected Return: {strategy.expected_return}%")
print(f"Max Loss: {strategy.max_loss}%")
```

### Working with Memory Systems

```python
"""
Example: Using episodic memory to track trades.
"""
from src.memory import EpisodicMemory
from src.data.schemas import TradeOutcome, StrategyType
from datetime import datetime

def track_trade_performance():
    """Track and analyze trade performance using episodic memory."""
    memory = EpisodicMemory()
    
    # Record a new trade
    trade = TradeOutcome(
        trade_id="TRADE-2024-001",
        symbol="AAPL",
        strategy_type=StrategyType.BULL_CALL_SPREAD,
        entry_date=datetime.now(),
        entry_price=180.50,
        quantity=10,  # 10 contracts
        original_rationale="Strong fundamentals and technical breakout"
    )
    
    memory.add_trade(trade)
    print(f"Trade {trade.trade_id} recorded")
    
    # Later, update with exit information
    trade_id = "TRADE-2024-001"
    memory.update_trade_outcome(
        trade_id=trade_id,
        exit_price=185.00,
        realized_pnl=2250.00,
        return_pct=15.0,
        outcome="win"
    )
    print(f"Trade {trade_id} closed with +15% return")
    
    # Retrieve trade history
    all_trades = memory.get_all_trades()
    print(f"\nTotal Trades: {len(all_trades)}")
    
    # Get trades for specific symbol
    aapl_trades = memory.get_trades_by_symbol("AAPL")
    print(f"AAPL Trades: {len(aapl_trades)}")
    
    # Get trades by outcome
    winning_trades = memory.get_trades_by_outcome("win")
    losing_trades = memory.get_trades_by_outcome("loss")
    
    print(f"\nPerformance Summary:")
    print(f"  Wins: {len(winning_trades)}")
    print(f"  Losses: {len(losing_trades)}")
    
    if winning_trades:
        avg_win = sum(t.return_pct for t in winning_trades if t.return_pct) / len(winning_trades)
        print(f"  Average Win: {avg_win:.1f}%")
    
    # Get recent trades
    recent = memory.get_recent_trades(limit=10)
    print(f"\nRecent {len(recent)} Trades:")
    for trade in recent:
        print(f"  {trade.symbol}: {trade.outcome} ({trade.return_pct or 0:.1f}%)")

# Usage
track_trade_performance()
```

### Error Handling Example

```python
"""
Example: Proper error handling with agents and data providers.
"""
import asyncio
from src.agents.market_intelligence import FundamentalsAnalyst
from src.data.providers import MarketDataProvider
from src.utils import get_logger

logger = get_logger(__name__)

async def safe_analysis(symbol: str):
    """Perform analysis with comprehensive error handling."""
    try:
        # Initialize
        agent = FundamentalsAnalyst()
        provider = MarketDataProvider()
        
        # Validate symbol first
        if not symbol or len(symbol) > 5:
            raise ValueError(f"Invalid symbol: {symbol}")
        
        # Check data availability
        current_price = provider.get_current_price(symbol)
        if current_price is None:
            logger.warning(f"No price data for {symbol}")
            return None
        
        # Perform analysis
        context = {
            "symbol": symbol,
            "market_data_provider": provider
        }
        
        report = await agent.analyze(context)
        
        # Validate output
        if report.confidence_level < 3:
            logger.warning(
                f"Low confidence analysis for {symbol}",
                confidence=report.confidence_level
            )
        
        return report
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return None
        
    except Exception as e:
        logger.error(
            f"Analysis failed for {symbol}",
            error=str(e),
            error_type=type(e).__name__
        )
        return None

# Usage with multiple symbols
async def batch_analysis(symbols):
    """Analyze multiple symbols with error handling."""
    results = {}
    
    for symbol in symbols:
        logger.info(f"Analyzing {symbol}")
        report = await safe_analysis(symbol)
        
        if report:
            results[symbol] = {
                "success": True,
                "confidence": report.confidence_level,
                "thesis": report.investment_thesis
            }
        else:
            results[symbol] = {
                "success": False,
                "error": "Analysis failed"
            }
    
    # Summary
    successful = sum(1 for r in results.values() if r["success"])
    print(f"\nAnalyzed {len(symbols)} symbols: {successful} successful")
    
    return results

# Run batch analysis
symbols = ["AAPL", "GOOGL", "INVALID", "MSFT", ""]
results = asyncio.run(batch_analysis(symbols))
```

### Backtesting Example

```python
"""
Example: Simple backtesting framework using historical data.
"""
from src.data.providers import MarketDataProvider
from datetime import datetime, timedelta
import pandas as pd

def backtest_simple_strategy(symbol: str, start_date: str, end_date: str):
    """
    Backtest a simple moving average crossover strategy.
    
    Strategy:
    - Buy when 50 SMA crosses above 200 SMA (golden cross)
    - Sell when 50 SMA crosses below 200 SMA (death cross)
    """
    provider = MarketDataProvider()
    
    # Get historical data
    history = provider.get_price_history(
        symbol,
        start=start_date,
        end=end_date,
        interval="1d"
    )
    
    if history.empty:
        print(f"No data for {symbol}")
        return None
    
    # Calculate moving averages
    history['SMA_50'] = history['Close'].rolling(window=50).mean()
    history['SMA_200'] = history['Close'].rolling(window=200).mean()
    
    # Identify crossovers
    history['Signal'] = 0
    history.loc[history['SMA_50'] > history['SMA_200'], 'Signal'] = 1  # Buy signal
    history.loc[history['SMA_50'] < history['SMA_200'], 'Signal'] = -1  # Sell signal
    
    # Detect signal changes
    history['Position'] = history['Signal'].diff()
    
    # Calculate returns
    trades = []
    position = None
    entry_price = None
    
    for idx, row in history.iterrows():
        if row['Position'] == 2:  # Buy signal (signal changed from -1 to 1)
            if position is None:
                position = 'long'
                entry_price = row['Close']
                trades.append({
                    'type': 'entry',
                    'date': idx,
                    'price': entry_price,
                    'signal': 'golden_cross'
                })
        
        elif row['Position'] == -2:  # Sell signal (signal changed from 1 to -1)
            if position == 'long':
                exit_price = row['Close']
                pnl_pct = ((exit_price - entry_price) / entry_price) * 100
                
                trades.append({
                    'type': 'exit',
                    'date': idx,
                    'price': exit_price,
                    'signal': 'death_cross',
                    'pnl_pct': pnl_pct
                })
                
                position = None
                entry_price = None
    
    # Calculate performance
    completed_trades = [t for t in trades if t['type'] == 'exit']
    
    if completed_trades:
        total_return = sum(t['pnl_pct'] for t in completed_trades)
        avg_return = total_return / len(completed_trades)
        winning_trades = [t for t in completed_trades if t['pnl_pct'] > 0]
        win_rate = len(winning_trades) / len(completed_trades)
        
        print(f"\nBacktest Results for {symbol}")
        print(f"Period: {start_date} to {end_date}")
        print(f"Total Trades: {len(completed_trades)}")
        print(f"Win Rate: {win_rate:.1%}")
        print(f"Average Return: {avg_return:.2f}%")
        print(f"Total Return: {total_return:.2f}%")
        
        return {
            'trades': trades,
            'total_trades': len(completed_trades),
            'win_rate': win_rate,
            'avg_return': avg_return,
            'total_return': total_return
        }
    else:
        print("No completed trades in backtest period")
        return None

# Usage
backtest_simple_strategy(
    "AAPL",
    start_date="2020-01-01",
    end_date="2024-01-01"
)
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
