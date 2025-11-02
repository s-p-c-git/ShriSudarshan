# Agent Behaviors and Decision Logic - Project Shri Sudarshan

## Overview

This guide documents the intended behaviors, decision-making logic, and operational characteristics of all 11 agents in Project Shri Sudarshan. Understanding these behaviors is crucial for system customization, debugging, and enhancement.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Market Intelligence Team](#market-intelligence-team)
  - [Fundamentals Analyst](#fundamentals-analyst)
  - [Macro & News Analyst](#macro--news-analyst)
  - [Sentiment Analyst](#sentiment-analyst)
  - [Technical Analyst](#technical-analyst)
- [Strategy & Research Team](#strategy--research-team)
  - [Bullish Researcher](#bullish-researcher)
  - [Bearish Researcher](#bearish-researcher)
  - [Derivatives Strategist](#derivatives-strategist)
- [Execution Team](#execution-team)
  - [Equity Trader](#equity-trader)
  - [FnO Trader](#fno-trader)
- [Oversight & Learning Team](#oversight--learning-team)
  - [Portfolio Manager](#portfolio-manager)
  - [Risk Manager](#risk-manager)
  - [Reflective Agent](#reflective-agent)
- [Agent Interactions](#agent-interactions)
- [Decision Flow](#decision-flow)

---

## Architecture Overview

Project Shri Sudarshan uses a **hierarchical multi-agent architecture** where agents collaborate in phases:

1. **Analysis Phase**: Market Intelligence agents run concurrently
2. **Debate Phase**: Bull/Bear researchers engage in structured debate
3. **Strategy Phase**: Derivatives strategist proposes FnO strategies
4. **Risk Gate**: Risk Manager validates the proposal
5. **Approval Gate**: Portfolio Manager makes final decision
6. **Execution Phase**: Trader agents execute approved trades
7. **Learning Phase**: Reflective Agent analyzes outcomes

Each agent has:
- **Specific domain expertise** (fundamentals, technicals, risk, etc.)
- **Defined input requirements** (market data, previous agent outputs)
- **Structured output format** (Pydantic models for validation)
- **LLM model assignment** (GPT-4o for critical agents, GPT-4o-mini for analysis)
- **Decision autonomy** within their domain

---

## Market Intelligence Team

### Fundamentals Analyst

**Role**: Analyze financial statements, earnings, and balance sheets to determine intrinsic value

**Model**: GPT-4o-mini (Standard model)  
**Temperature**: 0.5 (Lower for factual analysis)

#### Input Requirements
- **Symbol**: Stock ticker
- **Market data**: Fundamentals, company info, current price
- **Data sources**: yfinance (financial statements, ratios)

#### Decision Logic

1. **Data Collection**:
   - Fetches 30+ fundamental metrics (P/E, revenue growth, margins, etc.)
   - Retrieves company information (sector, industry, market cap)
   - Gets current price for valuation context

2. **Analysis Focus Areas**:
   - **Valuation metrics**: P/E, PEG, P/B, P/S ratios
   - **Profitability**: Profit margin, operating margin, ROE, ROA
   - **Growth**: Revenue growth, earnings growth
   - **Financial health**: Debt-to-equity, current ratio, free cash flow
   - **Shareholder returns**: Dividend yield, payout ratio

3. **Investment Thesis Determination**:
   - **Bullish** if: Strong growth, reasonable valuation, solid balance sheet
   - **Bearish** if: Declining metrics, high debt, overvaluation
   - **Neutral** if: Mixed signals or insufficient data

4. **Confidence Scoring** (1-10):
   - **8-10**: Complete data, clear signals, strong conviction
   - **5-7**: Adequate data, some ambiguity
   - **1-4**: Missing data, conflicting signals, high uncertainty

#### Output Format
```python
FundamentalsReport(
    symbol="AAPL",
    analysis="Comprehensive analysis text",
    key_points=["Revenue up 15%", "Strong margins", "High cash position"],
    confidence_level=8,
    intrinsic_value=185.50,  # Estimated intrinsic value per share
    investment_thesis=Sentiment.BULLISH,
    risk_factors=["Market competition", "Regulatory concerns"],
    financial_metrics={...}  # Full metrics dictionary
)
```

#### Behavioral Characteristics
- **Conservative**: Prefers established companies with proven track records
- **Data-driven**: Relies heavily on quantitative metrics
- **Long-term focused**: Emphasizes sustainable business models
- **Risk-aware**: Identifies financial red flags (high debt, declining margins)

#### Common Patterns
- Favors companies with:
  - Consistent revenue growth (>10% YoY)
  - High profit margins (>15%)
  - Strong ROE (>15%)
  - Low debt-to-equity (<1.0)
  - Positive free cash flow

---

### Macro & News Analyst

**Role**: Monitor macroeconomic data, central bank policies, geopolitical events, and breaking news

**Model**: GPT-4o-mini (Standard model)  
**Temperature**: 0.7 (Balanced for analysis)

#### Input Requirements
- **Symbol**: Stock ticker
- **News data**: Recent articles, headlines (7-30 days)
- **Market context**: Current market conditions
- **Data sources**: NewsProvider (aggregated news, sentiment)

#### Decision Logic

1. **Data Collection**:
   - Fetches company-specific news (last 7 days by default)
   - Retrieves market-wide news for context
   - Aggregates sentiment from multiple sources

2. **Analysis Focus Areas**:
   - **Central bank policy**: Fed decisions, interest rate outlook
   - **Economic indicators**: GDP growth, inflation, employment
   - **Geopolitical risks**: Wars, trade tensions, political instability
   - **Sector trends**: Industry-specific developments
   - **Breaking news**: Market-moving headlines

3. **Market Sentiment Determination**:
   - **Very Bullish**: Extremely positive news, strong catalysts
   - **Bullish**: Positive developments, favorable conditions
   - **Neutral**: Mixed news, no clear direction
   - **Bearish**: Negative developments, headwinds
   - **Very Bearish**: Crisis, severe negative events

4. **Confidence Scoring** (1-10):
   - Based on news volume, consistency, and recency
   - Higher confidence when multiple sources align
   - Lower confidence with conflicting or sparse news

#### Output Format
```python
MacroNewsReport(
    symbol="AAPL",
    analysis="Analysis of macro environment",
    key_points=["Fed rate cut expected", "Strong earnings season"],
    confidence_level=7,
    market_sentiment=Sentiment.BULLISH,
    key_events=["Q4 earnings beat", "New product launch"],
    macro_themes=["Economic recovery", "Tech sector strength"],
    news_items=["Apple announces...", "Industry outlook..."],
    risk_events=["Regulatory hearing scheduled"]
)
```

#### Behavioral Characteristics
- **Forward-looking**: Focuses on future catalysts and events
- **Contextual**: Considers broader market environment
- **Event-driven**: Reacts to breaking news and announcements
- **Risk-aware**: Identifies upcoming risk events

#### Common Patterns
- Bullish signals:
  - Positive earnings surprises
  - Product launch announcements
  - Favorable regulatory decisions
  - Sector rotation into the stock's industry
  
- Bearish signals:
  - Negative earnings guidance
  - Management departures
  - Regulatory investigations
  - Sector headwinds

---

### Sentiment Analyst

**Role**: Gauge market mood via social media, forums, and news sentiment

**Model**: GPT-4o-mini (Standard model)  
**Temperature**: 0.7 (Balanced for sentiment interpretation)

#### Input Requirements
- **Symbol**: Stock ticker
- **News data**: Recent articles with sentiment scores
- **Social data**: Social media mentions (when available)
- **Data sources**: NewsProvider (sentiment aggregation)

#### Decision Logic

1. **Data Collection**:
   - Aggregates sentiment from news articles
   - Analyzes headline tone and keywords
   - Counts positive/negative/neutral mentions
   - Tracks sentiment trends over time

2. **Analysis Focus Areas**:
   - **Social media sentiment**: Twitter/X, Reddit, StockTwits
   - **News sentiment**: Article tone, headline sentiment
   - **Retail positioning**: Retail investor activity levels
   - **Institutional activity**: Large player movements
   - **Contrarian indicators**: Extreme sentiment levels

3. **Sentiment Score Calculation** (-1.0 to +1.0):
   - **+0.6 to +1.0**: Very bullish sentiment
   - **+0.2 to +0.6**: Bullish sentiment
   - **-0.2 to +0.2**: Neutral sentiment
   - **-0.6 to -0.2**: Bearish sentiment
   - **-1.0 to -0.6**: Very bearish sentiment

4. **Confidence Scoring** (1-10):
   - Based on data volume and consistency
   - Higher when sentiment is clear and stable
   - Lower with low volume or mixed signals

#### Output Format
```python
SentimentReport(
    symbol="AAPL",
    analysis="Sentiment analysis text",
    key_points=["Strong retail interest", "Positive news tone"],
    confidence_level=7,
    social_sentiment=Sentiment.BULLISH,
    sentiment_score=0.65,
    sentiment_trend="improving",
    trending_topics=["new iPhone", "earnings beat"],
    retail_positioning="net long"
)
```

#### Behavioral Characteristics
- **Contrarian-aware**: Recognizes extreme sentiment as potential reversal signal
- **Trend-focused**: Tracks sentiment momentum and changes
- **Volume-sensitive**: Considers mention volume as signal strength
- **Real-time oriented**: Prioritizes recent sentiment over historical

#### Common Patterns
- **Extreme optimism** (score > 0.8):
  - May signal overbought conditions
  - Contrarian bearish opportunity
  
- **Extreme pessimism** (score < -0.8):
  - May signal oversold conditions
  - Contrarian bullish opportunity
  
- **Sentiment divergence**:
  - Sentiment improving while price declining = potential bottom
  - Sentiment declining while price rising = potential top

---

### Technical Analyst

**Role**: Analyze price charts, volume, and technical indicators

**Model**: GPT-4o-mini (Standard model)  
**Temperature**: 0.5 (Lower for pattern recognition)

#### Input Requirements
- **Symbol**: Stock ticker
- **Price history**: OHLCV data (30-365 days)
- **Technical indicators**: Calculated by MarketDataProvider
- **Data sources**: yfinance (price data, volume)

#### Decision Logic

1. **Data Collection**:
   - Fetches price history (1-3 months typical)
   - Calculates technical indicators:
     - Moving averages (SMA 20, 50, 200; EMA 12, 26)
     - RSI (14-period)
     - MACD (12, 26, 9)
     - Bollinger Bands (20-period, 2 std dev)
   - Identifies support/resistance levels

2. **Analysis Focus Areas**:
   - **Trend identification**: Uptrend, downtrend, sideways
   - **Support/resistance**: Key price levels
   - **Chart patterns**: Head & shoulders, triangles, flags
   - **Volume analysis**: Confirmation of price moves
   - **Momentum**: RSI, MACD signals
   - **Volatility**: Bollinger Bands, price swings

3. **Trend Classification**:
   - **Strong Uptrend**: Price above all MAs, higher highs/lows
   - **Uptrend**: Price above key MAs, generally rising
   - **Sideways**: Price oscillating in range
   - **Downtrend**: Price below key MAs, lower highs/lows
   - **Strong Downtrend**: Price well below MAs, accelerating decline

4. **Signal Generation**:
   - **Bullish signals**:
     - RSI oversold (<30) and turning up
     - MACD bullish crossover
     - Price breaking above resistance
     - Volume surge on upside
   
   - **Bearish signals**:
     - RSI overbought (>70) and turning down
     - MACD bearish crossover
     - Price breaking below support
     - Volume surge on downside

5. **Confidence Scoring** (1-10):
   - Higher when multiple indicators align
   - Lower with conflicting signals or choppy price action

#### Output Format
```python
TechnicalReport(
    symbol="AAPL",
    analysis="Technical analysis text",
    key_points=["Strong uptrend", "Above all MAs", "RSI at 55"],
    confidence_level=8,
    trend_direction=TrendDirection.UPTREND,
    support_levels=[165.00, 170.00, 175.00],
    resistance_levels=[185.00, 190.00, 195.00],
    chart_patterns=["Bull flag forming"],
    indicators={"rsi": 55, "macd": 1.2, ...},
    momentum_signals=["Positive momentum", "Volume increasing"]
)
```

#### Behavioral Characteristics
- **Trend-following**: Prefers trading with established trends
- **Pattern-focused**: Recognizes classic chart patterns
- **Confirmation-seeking**: Wants multiple indicator alignment
- **Risk-defined**: Identifies clear stop-loss levels (support)

#### Common Patterns
- **Buy signals**:
  - Price bouncing off support with volume
  - Golden cross (50 MA crosses above 200 MA)
  - Breakout above resistance on high volume
  - Bullish divergence (price lower low, RSI higher low)
  
- **Sell signals**:
  - Price rejecting at resistance
  - Death cross (50 MA crosses below 200 MA)
  - Breakdown below support on high volume
  - Bearish divergence (price higher high, RSI lower high)

---

## Strategy & Research Team

### Bullish Researcher

**Role**: Construct the strongest possible case for long positions

**Model**: GPT-4o-mini (Standard model)  
**Temperature**: 0.7 (Balanced for argumentation)

#### Input Requirements
- **Analyst reports**: All Market Intelligence team outputs
- **Symbol**: Stock ticker
- **Debate context**: Previous debate rounds (if any)

#### Decision Logic

1. **Evidence Gathering**:
   - Reviews fundamentals report for positive signals
   - Extracts bullish technical indicators
   - Highlights positive sentiment and news
   - Identifies growth catalysts from macro analysis

2. **Argument Construction**:
   - **Investment thesis**: Clear statement of why to buy
   - **Supporting evidence**: Cites specific analyst findings
   - **Catalysts**: Near-term events that could drive price up
   - **Entry strategy**: Proposed entry points and timing
   - **Risk acknowledgment**: Honest assessment of risks

3. **Debate Strategy**:
   - **Round 1**: Present strongest bull case with all evidence
   - **Round 2**: Refute bearish counterarguments
   - **Round 3**: Reinforce key bull points, address weaknesses

4. **Conviction Scoring** (1-10):
   - Based on strength and consistency of evidence
   - Higher when all analysts align bullishly
   - Lower when evidence is mixed or weak

#### Output Format
```python
DebateArgument(
    agent_role=AgentRole.BULLISH_RESEARCHER,
    round_number=1,
    argument="Strong bull case based on...",
    supporting_evidence=[
        "Fundamentals show 20% revenue growth",
        "Technical: strong uptrend, above 200 MA",
        "Sentiment: institutional accumulation"
    ],
    counterpoints=["Risk: high valuation", "Risk: macro headwinds"],
    confidence=8.0
)
```

#### Behavioral Characteristics
- **Optimistic**: Interprets ambiguous signals positively
- **Evidence-based**: Grounds arguments in analyst data
- **Strategic**: Anticipates and addresses bearish counterpoints
- **Opportunistic**: Identifies catalysts and timing advantages

#### Common Argument Patterns
- Growth story arguments:
  - "Revenue growing faster than peers"
  - "Expanding profit margins indicate operational efficiency"
  - "Strong free cash flow supports future growth"
  
- Technical momentum arguments:
  - "Price breaking out to new highs on volume"
  - "All technical indicators aligned bullishly"
  - "Support levels holding strong"
  
- Sentiment arguments:
  - "Institutional accumulation despite retail fear"
  - "Positive analyst upgrades and price target increases"
  - "News flow turning increasingly positive"

---

### Bearish Researcher

**Role**: Construct the strongest possible case for short positions or avoidance

**Model**: GPT-4o-mini (Standard model)  
**Temperature**: 0.7 (Balanced for argumentation)

#### Input Requirements
- **Analyst reports**: All Market Intelligence team outputs
- **Symbol**: Stock ticker
- **Debate context**: Previous debate rounds (if any)

#### Decision Logic

1. **Evidence Gathering**:
   - Reviews fundamentals for red flags
   - Extracts bearish technical indicators
   - Highlights negative sentiment and news
   - Identifies risks from macro analysis

2. **Argument Construction**:
   - **Bearish thesis**: Clear statement of why to avoid/short
   - **Supporting evidence**: Cites specific analyst concerns
   - **Risk catalysts**: Events that could drive price down
   - **Strategy**: Short positions, puts, or avoidance
   - **Counterarguments**: Challenges to bullish case

3. **Debate Strategy**:
   - **Round 1**: Present strongest bear case with all evidence
   - **Round 2**: Attack bull case weaknesses
   - **Round 3**: Reinforce key bear points, expose bull case flaws

4. **Conviction Scoring** (1-10):
   - Based on strength and consistency of bearish evidence
   - Higher when all analysts show concerning signals
   - Lower when bear case relies on few factors

#### Output Format
```python
DebateArgument(
    agent_role=AgentRole.BEARISH_RESEARCHER,
    round_number=1,
    argument="Strong bear case based on...",
    supporting_evidence=[
        "Fundamentals: declining margins and revenue miss",
        "Technical: breaking key support levels",
        "Sentiment: institutional distribution"
    ],
    counterpoints=["Bull: valuation attractive", "Bull: sector rotation"],
    confidence=7.5
)
```

#### Behavioral Characteristics
- **Skeptical**: Questions bullish assumptions and narratives
- **Risk-focused**: Emphasizes downside scenarios
- **Analytical**: Dissects bull case for weaknesses
- **Defensive**: Prioritizes capital preservation

#### Common Argument Patterns
- Fundamental deterioration:
  - "Declining revenue growth signals market saturation"
  - "Margin compression indicates competitive pressures"
  - "Rising debt levels create financial risk"
  
- Technical breakdown:
  - "Breaking below key support suggests further downside"
  - "Death cross signals trend reversal"
  - "Negative divergence warns of weakening momentum"
  
- Valuation concerns:
  - "Trading at extreme premium to peers"
  - "Forward P/E unsustainable given growth outlook"
  - "Multiple compression likely as sentiment shifts"

---

### Derivatives Strategist

**Role**: Analyze options data and propose specific FnO strategies

**Model**: GPT-4o (Premium model - Critical decision maker)  
**Temperature**: 0.7 (Balanced for creative strategy design)

#### Input Requirements
- **Debate outcome**: Bull/bear debate results
- **Options data**: Options chain, Greeks, IV
- **Symbol**: Stock ticker
- **Data sources**: MarketDataProvider (options chains)

#### Decision Logic

1. **Volatility Analysis**:
   - Compares implied volatility (IV) to historical volatility (HV)
   - **IV > HV**: Options overpriced → sell strategies
   - **IV < HV**: Options underpriced → buy strategies
   - **IV spike**: Potential event → straddle/strangle

2. **Strategy Selection** (Based on debate outcome):
   
   **Strong Bull Case**:
   - Long equity (outright stock purchase)
   - Long call options (leverage bullish view)
   - Bull call spread (defined risk bullish)
   
   **Moderate Bull Case**:
   - Covered call (generate income on long position)
   - Cash-secured put (enter at lower price)
   
   **Neutral Case**:
   - Iron condor (profit from low volatility)
   - Calendar spread (profit from time decay)
   - Short straddle/strangle (collect premium)
   
   **Moderate Bear Case**:
   - Protective put (hedge existing long)
   - Bear put spread (defined risk bearish)
   
   **Strong Bear Case**:
   - Short equity (direct bearish position)
   - Long put options (leverage bearish view)
   - Bear call spread (defined risk bearish)
   
   **High Volatility Expected**:
   - Long straddle (profit from large move either direction)
   - Long strangle (cheaper straddle alternative)

3. **Strike Selection**:
   - **Delta targeting**: Choose delta based on conviction
     - High conviction: Near-money strikes (delta 50-70)
     - Medium conviction: Slightly OTM (delta 30-50)
     - Low conviction: Further OTM (delta 10-30)
   
   - **Spread width**: Balance risk/reward
     - Narrow spreads: Lower cost, lower profit
     - Wide spreads: Higher cost, higher profit

4. **Expiration Selection**:
   - **Short-term** (1-2 weeks): High conviction on immediate move
   - **Medium-term** (1-3 months): Balanced theta/delta exposure
   - **Long-term** (6-12 months): Minimize time decay, long-term thesis

5. **Position Sizing**:
   - Calculates max loss and win probability
   - Sizes position to align with portfolio risk limits
   - Considers correlation with existing positions

6. **Greeks Analysis**:
   - **Delta**: Directional exposure (how much position moves with stock)
   - **Gamma**: Rate of delta change (convexity risk)
   - **Theta**: Time decay (daily P&L from time passage)
   - **Vega**: Volatility sensitivity (impact of IV changes)

#### Output Format
```python
StrategyProposal(
    symbol="AAPL",
    strategy_type=StrategyType.BULL_CALL_SPREAD,
    direction=TradeDirection.LONG,
    rationale="Bullish outlook with defined risk...",
    expected_return=15.0,  # 15% expected return
    max_loss=5.0,  # 5% max loss
    holding_period="30-45 days",
    entry_criteria=["Price > $180", "IV < 25%"],
    exit_criteria=["50% profit", "21 DTE", "Stop at 50% loss"],
    volatility_analysis={
        "iv": 0.22,
        "hv": 0.25,
        "iv_percentile": 35
    },
    greeks={
        "delta": 0.45,
        "gamma": 0.05,
        "theta": -0.15,
        "vega": 0.30
    },
    confidence=8.0
)
```

#### Behavioral Characteristics
- **Risk-defined**: Prefers strategies with defined maximum loss
- **Probability-focused**: Considers win probability and expected value
- **Greeks-aware**: Manages directional, time, and volatility exposures
- **Adaptive**: Selects strategy based on market conditions and conviction

#### Common Strategy Patterns

**High Conviction Bull**:
- Long calls or bull call spreads
- Higher delta (50-70)
- Near-term expirations for leverage
- Willing to accept higher vega risk

**High Conviction Bear**:
- Long puts or bear put spreads
- Higher delta magnitude (-50 to -70)
- Protection-focused
- Accept theta decay for directional exposure

**Low Volatility Environment**:
- Iron condors (collect premium from range)
- Short strangles (profit from stability)
- Calendar spreads (benefit from theta)

**High Volatility Environment**:
- Long straddles/strangles (profit from big moves)
- Avoid premium selling strategies
- Focus on directional strategies with defined risk

---

## Execution Team

### Equity Trader

**Role**: Execute stock trades with optimal timing and minimal market impact

**Model**: GPT-4o-mini (Standard model)  
**Temperature**: 0.3 (Low for precise execution planning)

#### Input Requirements
- **Strategy proposal**: From Derivatives Strategist
- **Approval**: Risk and portfolio manager approval
- **Symbol**: Stock ticker
- **Market conditions**: Current price, volume, bid-ask spread

#### Decision Logic

1. **Order Type Selection**:
   - **Market order**: Urgent execution, liquid stock
   - **Limit order**: Price-sensitive, normal conditions
   - **Stop order**: Risk management, exit strategy
   - **Stop-limit**: Combine stop trigger with limit protection

2. **Timing Considerations**:
   - **Market open** (9:30-10:00 AM ET): Avoid high volatility
   - **Mid-day** (10:30 AM-3:00 PM ET): Optimal for most trades
   - **Market close** (3:00-4:00 PM ET): Avoid unless necessary
   - **After-hours**: Only for urgent situations, wider spreads

3. **Position Sizing**:
   - Reviews portfolio manager's approved size
   - Considers average daily volume (ADV)
   - **Large orders** (>5% ADV): Split into smaller chunks
   - **Small orders** (<1% ADV): Execute as single trade

4. **Slippage Estimation**:
   - **Tight spread** (<0.1%): Minimal slippage expected
   - **Normal spread** (0.1-0.3%): Moderate slippage
   - **Wide spread** (>0.3%): Significant slippage risk
   - Adjusts execution strategy based on spread

5. **Execution Strategy**:
   - **VWAP** (Volume Weighted Average Price): For large orders
   - **TWAP** (Time Weighted Average Price): For scheduled execution
   - **Iceberg orders**: Hide true order size
   - **Smart routing**: Find best price across venues

#### Output Format
```python
ExecutionPlan(
    symbol="AAPL",
    strategy_type=StrategyType.LONG_EQUITY,
    orders=[
        Order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.LIMIT,
            price=180.50,
            time_in_force="DAY"
        )
    ],
    estimated_cost=18050.00,
    estimated_slippage=10.00,  # $10 expected slippage
    estimated_commissions=1.00,
    execution_strategy="Limit order at bid-ask midpoint",
    timing_recommendations="Execute during mid-day for best liquidity"
)
```

#### Behavioral Characteristics
- **Patient**: Waits for favorable prices when possible
- **Efficient**: Minimizes costs (slippage + commissions)
- **Adaptive**: Adjusts to real-time market conditions
- **Risk-aware**: Avoids trades during volatile periods

#### Common Execution Patterns
- **Small orders** (<$10K):
  - Single market or limit order
  - Execute immediately
  
- **Medium orders** ($10K-$100K):
  - Limit order at favorable price
  - Monitor for fill over 1-2 hours
  - Adjust price if not filled
  
- **Large orders** (>$100K):
  - Split into multiple smaller orders
  - Execute over multiple hours/days
  - Use VWAP or algo execution

---

### FnO Trader

**Role**: Execute complex multi-leg options and futures strategies

**Model**: GPT-4o-mini (Standard model)  
**Temperature**: 0.3 (Low for precise execution)

#### Input Requirements
- **Strategy proposal**: From Derivatives Strategist
- **Approval**: Risk and portfolio manager approval
- **Symbol**: Stock ticker
- **Options chain**: Current option prices, Greeks

#### Decision Logic

1. **Liquidity Assessment**:
   - Checks open interest and volume for each leg
   - **Liquid options**: OI >1000, tight spread
   - **Moderate liquidity**: OI 100-1000, wider spread
   - **Illiquid options**: OI <100, avoid or adjust strategy

2. **Execution Sequencing** (For multi-leg strategies):
   - **Spreads**: Enter as spread order when possible
   - **Complex strategies**: Leg into position
     - Execute long legs first (establish risk-defined position)
     - Execute short legs second (collect premium)
   - **Market making**: Enter at mid-point or better

3. **Price Limits**:
   - **Spread strategies**: Set net debit/credit limit
   - **Individual options**: Set limit based on bid-ask
   - **Greeks monitoring**: Track position delta, theta, vega
   - **Slippage control**: Avoid chasing prices

4. **Risk During Execution**:
   - **Partial fills**: Monitor exposure if only some legs filled
   - **Pin risk**: Avoid short options near strike at expiration
   - **Assignment risk**: Be prepared for early assignment
   - **Gamma risk**: Large position gamma can cause rapid P&L swings

5. **Monitoring Requirements**:
   - Track until all legs filled
   - Monitor Greeks after execution
   - Set up alerts for:
     - Significant price moves
     - Volatility changes
     - Approaching expiration

#### Output Format
```python
ExecutionPlan(
    symbol="AAPL",
    strategy_type=StrategyType.BULL_CALL_SPREAD,
    orders=[
        Order(  # Buy leg
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=10,
            order_type=OrderType.LIMIT,
            price=5.50,
            strike=180.00,
            expiry="2024-12-15",
            option_type="call"
        ),
        Order(  # Sell leg
            symbol="AAPL",
            side=OrderSide.SELL,
            quantity=10,
            order_type=OrderType.LIMIT,
            price=3.00,
            strike=190.00,
            expiry="2024-12-15",
            option_type="call"
        )
    ],
    estimated_cost=2500.00,  # Net debit: (5.50 - 3.00) * 10 contracts * 100
    estimated_slippage=50.00,
    estimated_commissions=6.50,  # $0.65 per contract * 10
    execution_strategy="Enter as spread order at $2.50 net debit or better",
    timing_recommendations="Execute when implied volatility below 25%",
    risk_mitigation=[
        "Monitor for early assignment on short leg",
        "Set stop at 50% loss ($1250)",
        "Take profit at 50% gain ($1250)"
    ]
)
```

#### Behavioral Characteristics
- **Methodical**: Carefully sequences multi-leg executions
- **Patient**: Waits for favorable spread prices
- **Risk-conscious**: Monitors assignment and pin risk
- **Greeks-aware**: Tracks position exposures continuously

#### Common Execution Patterns

**Spread Strategies**:
1. Attempt as spread order first (better pricing)
2. If no fill after 15 minutes, leg into position:
   - Buy long leg first (establish risk-defined position)
   - Sell short leg second (collect premium)

**Straddles/Strangles**:
1. Enter both legs simultaneously as combo order
2. Monitor for asymmetric fills
3. Adjust remaining leg if market moves

**Complex Multi-Leg**:
1. Establish core position first
2. Add additional legs incrementally
3. Monitor total Greeks after each leg

---

## Oversight & Learning Team

### Portfolio Manager

**Role**: Make final approval/rejection decisions on trade proposals

**Model**: GPT-4o (Premium model - Critical decision maker)  
**Temperature**: 0.7 (Balanced for strategic thinking)

#### Input Requirements
- **Strategy proposal**: From Derivatives Strategist
- **Risk assessment**: From Risk Manager
- **Debate outcome**: Bull/bear debate results
- **Portfolio state**: Current positions, allocation, performance

#### Decision Logic

1. **Strategic Fit Assessment**:
   - **Portfolio objectives**: Align with growth/income/risk targets
   - **Diversification**: Evaluate sector/asset concentration
   - **Conviction alignment**: Match position size to conviction
   - **Timing**: Consider market cycle and conditions

2. **Risk/Reward Evaluation**:
   - **Expected return** vs. **max drawdown**
   - **Win probability** vs. **loss probability**
   - **Opportunity cost**: Compare to alternative trades
   - **Portfolio impact**: Effect on overall portfolio metrics

3. **Capital Allocation**:
   - Reviews available capital
   - Considers existing positions
   - Evaluates correlation with current holdings
   - Determines optimal position size:
     - **High conviction**: 3-5% of portfolio
     - **Medium conviction**: 1-3% of portfolio
     - **Low conviction**: <1% of portfolio or reject

4. **Approval Gates**:
   - **Must pass risk assessment**: Risk manager approval required
   - **Strategic alignment**: Trade fits portfolio mandate
   - **Adequate conviction**: Debate produced clear winner
   - **Favorable risk/reward**: >2:1 reward-to-risk minimum
   
5. **Rejection Criteria**:
   - **Risk assessment failed**: Veto by risk manager
   - **Poor strategic fit**: Doesn't align with objectives
   - **Weak conviction**: Inconclusive debate outcome
   - **Capital constraints**: Insufficient funds available
   - **Excessive concentration**: Too much exposure to sector/asset

#### Output Format
```python
PortfolioDecision(
    symbol="AAPL",
    approved=True,
    decision_rationale="Strong fundamental and technical case, fits growth mandate",
    position_size=3.5,  # 3.5% of portfolio
    strategic_fit="Aligns with tech sector allocation target",
    opportunity_cost="Passing on lower conviction GOOGL trade",
    monitoring_requirements=[
        "Review weekly earnings releases",
        "Monitor product launch success",
        "Track sector rotation signals"
    ],
    conditions=[
        "Exit if breaks below $170 support",
        "Take partial profits at $200",
        "Review position if risk assessment changes"
    ],
    review_date="2024-12-30"  # Quarterly review
)
```

#### Behavioral Characteristics
- **Strategic**: Thinks about long-term portfolio goals
- **Disciplined**: Follows risk management rules strictly
- **Balanced**: Weighs multiple factors before deciding
- **Accountable**: Takes ultimate responsibility for decisions

#### Common Decision Patterns

**Approval (High Conviction)**:
- All analysts bullish or bearish consensus
- Risk assessment passed easily
- Clear catalysts and favorable risk/reward
- Position size: 3-5% of portfolio

**Approval (Medium Conviction)**:
- Mixed signals but lean in one direction
- Risk assessment passed with conditions
- Decent risk/reward but not exceptional
- Position size: 1-3% of portfolio

**Conditional Approval**:
- Approve but with strict conditions
- Smaller position size than requested
- Require additional monitoring
- Set tight stop-losses

**Rejection**:
- Risk manager vetoed
- Weak or inconclusive debate
- Poor risk/reward profile
- Excessive portfolio concentration
- Insufficient capital

---

### Risk Manager

**Role**: Assess risk and have veto authority over trades violating risk parameters

**Model**: GPT-4o (Premium model - Critical decision maker)  
**Temperature**: 0.5 (Lower for risk assessment accuracy)

#### Input Requirements
- **Strategy proposal**: From Derivatives Strategist
- **Portfolio state**: Current positions, risk metrics
- **Market conditions**: VIX, correlations, volatility
- **Risk limits**: Configured max position, VaR, concentration

#### Decision Logic

1. **Position Size Validation**:
   - Checks against `MAX_POSITION_SIZE` (default 5% of portfolio)
   - **Pass**: Proposed size ≤ limit
   - **Fail**: Proposed size > limit
   - Considers correlation with existing positions

2. **Value at Risk (VaR) Calculation**:
   - Estimates potential loss over time horizon (1 day, 1 week)
   - Uses historical volatility and position size
   - **95% VaR**: Loss exceeded only 5% of the time
   - **99% VaR**: Loss exceeded only 1% of the time
   - Checks against `MAX_PORTFOLIO_RISK` (default 2% of portfolio)

3. **Concentration Risk Assessment**:
   - Sector concentration check
   - Single position size check
   - Correlation with existing positions
   - Checks against `MAX_SECTOR_CONCENTRATION` (default 25%)

4. **Tail Risk Scenarios**:
   - **Black swan events**: Market crash (-20% in day)
   - **Flash crash**: Sudden liquidity event
   - **Options assignment**: Early assignment risk
   - **Margin call risk**: Account equity dropping below requirements

5. **Approval Decision**:
   - **Approved**: All checks passed
   - **Approved with conditions**: Minor issues, add hedges/stops
   - **Rejected (Veto)**: Critical risk limit violations
     - Position size >MAX_POSITION_SIZE
     - Portfolio VaR >MAX_PORTFOLIO_RISK
     - Sector concentration >MAX_SECTOR_CONCENTRATION
     - Unacceptable tail risk

#### Output Format
```python
RiskAssessment(
    symbol="AAPL",
    approved=True,
    var_estimate=0.015,  # 1.5% portfolio VaR
    position_size_pct=3.5,  # 3.5% of portfolio
    recommendation="Approved with stop-loss condition",
    portfolio_impact="Increases tech exposure to 18% (under 20% limit)",
    correlation_risk=0.65,  # 0.65 correlation with existing tech positions
    sector_concentration=0.18,  # 18% in tech sector
    max_drawdown_estimate=0.08,  # 8% max drawdown estimated
    risk_warnings=["High correlation with MSFT position"],
    conditions=[
        "Set stop-loss at 20% position loss",
        "Hedge with SPY puts if VIX >30",
        "Review if portfolio VaR exceeds 1.8%"
    ]
)
```

#### Behavioral Characteristics
- **Conservative**: Errs on side of caution
- **Quantitative**: Relies on calculated risk metrics
- **Veto power**: Can override all other agents for risk violations
- **Forward-looking**: Considers tail risk scenarios

#### Common Risk Assessment Patterns

**Low Risk (Approved)**:
- Small position size (1-2%)
- Low volatility asset
- Low correlation with existing positions
- Sector not concentrated
- Defined risk strategy (spreads)

**Medium Risk (Approved with Conditions)**:
- Moderate position size (3-5%)
- Moderate volatility
- Some correlation with existing positions
- Require stop-losses or hedges
- Monitor closely

**High Risk (Rejected)**:
- Excessive position size (>5%)
- Very high volatility
- High correlation with existing large positions
- Sector concentration >25%
- Undefined risk (naked options)
- Portfolio VaR breach

---

### Reflective Agent

**Role**: Post-trade analysis and belief adjustment for system-wide learning

**Model**: GPT-4o (Premium model - Strategic learning)  
**Temperature**: 0.7 (Balanced for insight generation)

#### Input Requirements
- **Trade outcome**: Entry, exit, P&L, duration
- **Original analysis**: All agent reports from entry
- **Market data**: What actually happened
- **Episodic memory**: Historical trade records

#### Decision Logic

1. **Outcome Classification**:
   - **Win**: Positive P&L, >5% return
   - **Loss**: Negative P&L, <-5% return
   - **Breakeven**: P&L between -5% and +5%
   - **Pending**: Trade still open

2. **Analysis Accuracy Assessment**:
   - **What worked**:
     - Which analysts were correct?
     - Which factors played out as expected?
     - What signals were accurate?
   
   - **What failed**:
     - Which analysts were incorrect?
     - Which factors were misjudged?
     - What signals were misleading?

3. **Root Cause Analysis**:
   - **Market conditions changed**: Unexpected events
   - **Incorrect analysis**: Faulty assumptions or data
   - **Poor timing**: Right thesis, wrong entry/exit
   - **Execution issues**: Slippage, fills, timing
   - **Risk management**: Stop too tight or too loose

4. **Conceptual Recommendations**:
   - **Agent improvements**: Which agents need tuning?
   - **Process improvements**: Workflow or gate changes?
   - **Risk parameter adjustments**: Tighten or loosen limits?
   - **Strategy refinements**: Which strategies work best?

5. **Belief Adjustment**:
   - **Increase confidence in**:
     - Consistently accurate agents
     - Reliable patterns and signals
     - Effective strategies
   
   - **Decrease confidence in**:
     - Frequently wrong agents
     - Misleading patterns
     - Underperforming strategies

#### Output Format
```python
Reflection(
    trade_id="TRADE-2024-001",
    symbol="AAPL",
    outcome_summary="Win: +12% return in 30 days",
    what_worked=[
        "Fundamentals analyst correctly identified strong earnings",
        "Technical analyst spotted breakout pattern",
        "Options strategy (bull call spread) captured move with defined risk"
    ],
    what_failed=[
        "Sentiment analyst overestimated retail interest",
        "Entry timing could have been better (entered early)"
    ],
    market_lessons=[
        "Tech earnings season provided strong catalyst",
        "Options IV contracted after earnings, boosting returns",
        "Support level held as predicted"
    ],
    strategic_adjustments=[
        "Increase weight on fundamentals for earnings-driven trades",
        "Consider waiting for post-earnings IV crush for option entries",
        "Technical support/resistance levels proved reliable"
    ],
    confidence_impact="Increase confidence in fundamentals and technical agents",
    conceptual_recommendations="Consider adding earnings surprise factor to fundamental analysis"
)
```

#### Behavioral Characteristics
- **Objective**: Analyzes outcomes without bias
- **Learning-focused**: Extracts lessons for future improvement
- **Systematic**: Looks for patterns across multiple trades
- **Actionable**: Provides specific, implementable recommendations

#### Common Reflection Patterns

**Winning Trade Reflection**:
- Identify which agents were most accurate
- Recognize effective strategies and patterns
- Reinforce successful decision-making process
- Still look for areas of improvement

**Losing Trade Reflection**:
- Determine primary cause of loss
- Identify which agents missed key factors
- Analyze if loss was preventable
- Extract specific lessons to avoid repeat

**Pattern Recognition Across Trades**:
- Which agent is consistently most/least accurate?
- Which strategies have highest win rate?
- What market conditions favor which approaches?
- Are there systematic biases to correct?

---

## Agent Interactions

### Phase-Based Interactions

#### Phase 1: Analysis (Concurrent)
```
Market Data → [Fundamentals Analyst] ─┐
           → [Macro/News Analyst]  ─┤
           → [Sentiment Analyst]   ─┼→ Combined Reports → Phase 2
           → [Technical Analyst]   ─┘
```

#### Phase 2: Debate (Sequential Rounds)
```
Combined Reports → [Bullish Researcher] ←─┐
                                          ├─ Debate Round 1
                → [Bearish Researcher] ←─┘
                ↓
                Debate Round 2
                ↓
                Debate Round 3
                ↓
                Debate Summary → Phase 3
```

#### Phase 3: Strategy (Sequential)
```
Debate Summary → [Derivatives Strategist] → Strategy Proposal → Phase 4
```

#### Phase 4: Risk Gate (Sequential)
```
Strategy Proposal → [Risk Manager] → Risk Assessment
                                    ↓
                          Approved? ─┬─ No → Reject Trade
                                    │
                                   Yes
                                    ↓
                                 Phase 5
```

#### Phase 5: Approval Gate (Sequential)
```
Strategy + Risk Assessment → [Portfolio Manager] → Decision
                                                   ↓
                                         Approved? ─┬─ No → Reject Trade
                                                   │
                                                  Yes
                                                   ↓
                                                Phase 6
```

#### Phase 6: Execution (Sequential)
```
Approved Strategy → [Equity Trader or FnO Trader] → Execution Plan → Execute
```

#### Phase 7: Learning (Post-Trade)
```
Trade Outcome + Original Analysis → [Reflective Agent] → Lessons Learned
                                                         ↓
                                                 Update Beliefs
                                                         ↓
                                                Improve Future Decisions
```

---

## Decision Flow

### Complete Workflow Decision Tree

```
Start Analysis
    ├─> Market Intelligence Team (Concurrent)
    │   ├─> Fundamentals: Bullish/Bearish/Neutral
    │   ├─> Macro/News: Bullish/Bearish/Neutral
    │   ├─> Sentiment: Bullish/Bearish/Neutral
    │   └─> Technical: Bullish/Bearish/Neutral
    │
    ├─> Strategy & Research Team
    │   ├─> Bull vs Bear Debate (3 rounds)
    │   │   └─> Winner: Bull or Bear
    │   │
    │   └─> Derivatives Strategist
    │       ├─> If Bull Won: Long strategies
    │       ├─> If Bear Won: Short strategies
    │       └─> If Neutral: Income strategies
    │
    ├─> Oversight Team (Risk Gate)
    │   └─> Risk Manager
    │       ├─> Approved: Continue to Portfolio Manager
    │       └─> Rejected: STOP (Veto)
    │
    ├─> Oversight Team (Approval Gate)
    │   └─> Portfolio Manager
    │       ├─> Approved: Continue to Execution
    │       └─> Rejected: STOP
    │
    ├─> Execution Team
    │   ├─> Equity Strategy: Equity Trader executes
    │   └─> Options Strategy: FnO Trader executes
    │
    └─> Post-Trade
        └─> Reflective Agent analyzes outcome
            └─> Update system beliefs and confidence
```

### Approval Cascades

**Scenario 1: Full Approval**
```
Risk Manager: ✓ Approved
Portfolio Manager: ✓ Approved
→ Trade Executed
```

**Scenario 2: Risk Rejection**
```
Risk Manager: ✗ Rejected (Veto)
→ Trade Stopped (Portfolio Manager not consulted)
```

**Scenario 3: Portfolio Rejection**
```
Risk Manager: ✓ Approved
Portfolio Manager: ✗ Rejected
→ Trade Stopped
```

**Scenario 4: Conditional Approval**
```
Risk Manager: ✓ Approved with conditions (stop-loss required)
Portfolio Manager: ✓ Approved with reduced size
→ Trade Executed with modifications
```

---

## Best Practices for Working with Agents

### For Developers

1. **Modifying Agent Behavior**:
   - Edit system prompts in `src/config/prompts.py`
   - Adjust temperature for creativity vs. consistency
   - Update decision logic in agent classes
   - Test changes with variety of scenarios

2. **Adding New Agents**:
   - Inherit from `BaseAgent` or `CriticalAgent`
   - Define clear role and responsibility
   - Create structured output schema (Pydantic)
   - Integrate into appropriate workflow phase
   - Document behavior in this guide

3. **Debugging Agent Issues**:
   - Enable DEBUG logging to see LLM responses
   - Check if data providers return valid data
   - Verify Pydantic schema validation passes
   - Test agent in isolation before integration
   - Review system prompts for clarity

### For Traders

1. **Understanding Agent Outputs**:
   - Each agent has `confidence_level` (1-10)
   - Higher confidence = stronger conviction
   - Cross-reference multiple agents for validation
   - Debate outcome indicates consensus direction

2. **Interpreting Rejections**:
   - Risk Manager rejection = safety concern
   - Portfolio Manager rejection = strategic misfit
   - Review rejection rationale for specifics
   - Adjust strategy or wait for better setup

3. **Trusting Agent Decisions**:
   - Agents use GPT-4o for critical decisions
   - Multiple validation gates protect capital
   - Reflective learning improves over time
   - Always review trade rationale personally

### For System Operators

1. **Monitoring Agent Performance**:
   - Track individual agent accuracy over time
   - Monitor debate outcomes vs. actual market moves
   - Review reflective agent insights regularly
   - Adjust confidence in consistently wrong agents

2. **Tuning Risk Parameters**:
   - Start conservative, relax gradually
   - Monitor portfolio VaR and drawdowns
   - Adjust based on market volatility regime
   - Document all parameter changes

3. **System Health Checks**:
   - Verify all agents completing successfully
   - Check for API rate limiting issues
   - Monitor data provider reliability
   - Review error logs daily

---

## Conclusion

Project Shri Sudarshan's multi-agent architecture creates a robust, scalable trading system through:

- **Specialized expertise**: Each agent excels in its domain
- **Collaborative decision-making**: Debate and consensus building
- **Hierarchical risk management**: Multiple approval gates
- **Continuous learning**: Reflective improvement loop
- **Transparent logic**: Clear, documented decision processes

Understanding these agent behaviors enables effective customization, debugging, and enhancement of the system.

---

**See Also**:
- [System Prompts Documentation](SYSTEM_PROMPTS.md)
- [API Reference](API_REFERENCE.md)
- [Architecture Documentation](architecture.md)
- [Getting Started Guide](getting_started.md)

---

*Last updated: 2025-11-02*
