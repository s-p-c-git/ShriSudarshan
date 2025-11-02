# Project Shri Sudarshan Architecture

## Overview

Project Shri Sudarshan is a sophisticated multi-agent LLM system for trading stocks and derivatives (Futures & Options). The architecture combines the team-based structure of TradingAgents with the risk management and learning capabilities of FinCon.

## System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                  LangGraph Orchestrator                      │
│              (State Machine & Workflow Engine)               │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Market   │───▶│Strategy &│───▶│Execution │
    │Intel Team│    │Research  │    │  Team    │
    └──────────┘    └──────────┘    └──────────┘
            │               │               │
            └───────────────┼───────────────┘
                            ▼
                    ┌──────────────┐
                    │  Oversight & │
                    │ Learning Team│
                    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │Memory System │
                    │ (3 Layers)   │
                    └──────────────┘
```

## Agent Teams

### 1. Market Intelligence Team

**Purpose**: Multi-modal data ingestion and initial analysis

**Agents**:
- **Fundamentals Analyst**: Analyzes financial statements, earnings, balance sheets
- **Macro & News Analyst**: Monitors economic data, central bank policies, geopolitical events
- **Sentiment Analyst**: Gauges market mood via social media, forums, news sentiment
- **Technical Analyst**: Analyzes price charts, volume, patterns, and indicators

**Execution**: Concurrent (all agents run in parallel)

**Output**: Structured analysis reports (JSON)

### 2. Strategy & Research Team

**Purpose**: Challenge and refine initial analyses into actionable strategies

**Agents**:
- **Bullish Researcher**: Constructs strongest case for long positions
- **Bearish Researcher**: Constructs strongest case for short/bearish positions
- **Derivatives Strategist**: Analyzes options data and proposes FnO strategies

**Execution**: Sequential debate mechanism (multiple rounds)

**Output**: Strategy proposal with debate transcript

### 3. Execution Team

**Purpose**: Practical implementation of approved strategies

**Agents**:
- **Equity Trader**: Executes stock trades with optimal timing and sizing
- **FnO Trader**: Executes complex multi-leg options and futures strategies

**Execution**: Sequential based on strategy type

**Output**: Execution plan with order specifications

### 4. Oversight & Learning Team

**Purpose**: Risk management, final approval, and system-wide learning

**Agents**:
- **Portfolio Manager**: Makes final approval/rejection decisions
- **Risk Manager**: Validates risk parameters, has veto authority
- **Reflective Agent**: Post-trade analysis and belief adjustment

**Execution**: Sequential (Risk → Portfolio → Learning)

**Output**: Approval decision and learning insights

## Workflow Phases

### Phase 1: Analysis
1. Market Intelligence agents run concurrently
2. Each produces structured report in their domain
3. Reports aggregated for next phase

### Phase 2: Debate & Strategy
1. Bullish and Bearish researchers engage in structured debate
2. Derivatives Strategist observes and formulates FnO strategy
3. Consolidated strategy proposal created

### Phase 3: Execution Planning
1. Relevant trader agents create detailed execution plan
2. Order types, limits, and timing specified
3. Contingency plans developed

### Phase 4: Risk Assessment
1. Risk Manager evaluates portfolio impact
2. Checks against risk parameters (VaR, concentration)
3. Approve or veto decision

### Phase 5: Portfolio Decision
1. Portfolio Manager reviews complete proposal
2. Makes final approval/rejection decision
3. Sets position sizing and monitoring requirements

### Phase 6: Execution
1. Trader agents execute approved orders
2. Interface with broker APIs
3. Monitor order fills

### Phase 7: Learning Loop
1. Trade outcome logged to episodic memory
2. Reflective Agent analyzes results
3. Conceptual insights fed back to Portfolio Manager

## Memory System

### Three-Layer Architecture

#### 1. Working Memory
- **Type**: In-memory (Redis optional)
- **Purpose**: Short-term state for ongoing analysis
- **Scope**: Current session only
- **TTL**: Until session completion
- **Contents**: 
  - Analysis context
  - Debate state
  - Pending orders
  - Session metadata

#### 2. Procedural Memory
- **Type**: Vector database (ChromaDB)
- **Purpose**: Successful workflows and patterns
- **Scope**: Long-term, searchable
- **Contents**:
  - Effective analysis workflows
  - Successful debate patterns
  - Optimal execution strategies
- **Access**: Similarity search

#### 3. Episodic Memory
- **Type**: SQL database (SQLite/PostgreSQL)
- **Purpose**: Historical trades and outcomes
- **Scope**: Permanent record
- **Contents**:
  - Trade details (entry, exit, P&L)
  - Original rationale
  - Market conditions
  - Reflective insights
- **Access**: Structured queries

## Technology Stack

### Core Framework
- **LangGraph**: Agent orchestration and state management
- **LangChain**: LLM chains and tools
- **OpenAI API**: LLM intelligence (GPT-4o, GPT-4o-mini)

### Data & Market
- **yfinance**: Stock market data
- **Alpha Vantage**: Alternative data source
- **Pandas/NumPy**: Data processing

### Memory
- **ChromaDB**: Vector database for procedural memory
- **SQLAlchemy**: ORM for episodic memory
- **Redis** (optional): Distributed working memory

### Development
- **Python 3.9+**: Primary language
- **Pydantic**: Data validation
- **pytest**: Testing framework
- **structlog**: Structured logging

## State Management

### LangGraph State
The workflow state (`TradingSystemState`) is passed between agents and contains:
- Input parameters (symbol, dates)
- Phase completion flags
- Agent outputs (reports, proposals, decisions)
- Error tracking
- Metadata (timestamps, current phase)

### State Transitions
- Deterministic flow through phases
- Conditional edges for approval gates
- Error handling and retry logic
- Checkpointing for long-running workflows

## Data Flow

```
Input (Symbol) 
    ↓
Market Data → Analysts → Reports
    ↓
Reports → Researchers → Debate → Strategy
    ↓
Strategy → Traders → Execution Plan
    ↓
Execution Plan → Risk Manager → Assessment
    ↓
Assessment (if approved) → Portfolio Manager → Decision
    ↓
Decision (if approved) → Traders → Orders
    ↓
Orders → Execution → Outcome
    ↓
Outcome → Reflective Agent → Insights
    ↓
Insights → Episodic Memory
```

## Risk Management

### Risk Parameters
- Maximum position size: 5% of portfolio
- Maximum portfolio risk (VaR): 2%
- Maximum sector concentration: 25%

### Risk Controls
1. **Pre-trade**: Risk Manager validation
2. **Veto authority**: Independent oversight
3. **Position sizing**: Dynamic based on confidence
4. **Monitoring**: Continuous position tracking
5. **Stop losses**: Automatic exit conditions

## Configuration

### Environment Variables
- API keys (OpenAI, data providers)
- Model selection (premium vs standard)
- Risk parameters
- Database connections
- Feature flags

### Flexibility
- Paper trading mode (default)
- Live trading mode (with confirmation)
- Concurrent vs sequential analysis
- Debate round limits
- Timeout configurations

## Extension Points

### Adding New Agents
1. Inherit from `BaseAgent` or `CriticalAgent`
2. Implement `analyze()` method
3. Define system prompt
4. Register in workflow

### Custom Strategies
1. Extend `StrategyProposal` schema
2. Add logic in Derivatives Strategist
3. Update execution team handlers

### Additional Data Sources
1. Create provider interface
2. Implement data fetching
3. Integrate into analyst workflows

## Future Enhancements

### Phase 2 Development
- [ ] Real-time data streaming
- [ ] Advanced backtesting engine
- [ ] Multi-symbol portfolio optimization
- [ ] Advanced options pricing models
- [ ] Machine learning for pattern recognition

### Phase 3 Development
- [ ] Alternative LLM providers
- [ ] Custom fine-tuned models
- [ ] Distributed execution (multiple servers)
- [ ] Web UI dashboard
- [ ] Performance analytics

## References

- **FinCon**: MQL5 article on hierarchical trading agents with risk control
- **TradingAgents**: Open-source collaborative trading framework
- **LangGraph**: Multi-agent orchestration framework
- **LangChain**: LLM application framework
