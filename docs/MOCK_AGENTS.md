# Mock Agents for Testing

This document explains how to use mock agents for testing agent modules without requiring LLM API access.

## Overview

The mock agent system provides deterministic, fast, and API-free testing of agent workflows. Mock agents inherit from `BaseAgent` and `CriticalAgent` but do not make actual LLM API calls.

## Key Features

- **No API Dependencies**: Tests run without OpenAI/Anthropic API keys
- **Fast Execution**: Each test completes in <0.1 seconds
- **Deterministic Results**: Same inputs always produce same outputs
- **Full Agent Coverage**: All 12 agents have mock implementations
- **Easy Integration**: Drop-in replacements via fixtures

## Mock Agent Classes

Located in `tests/mock_agents.py`:

### Market Intelligence Team (4 agents)
- `MockFundamentalsAnalyst`: Returns realistic fundamental analysis
- `MockTechnicalAnalyst`: Returns technical indicators and patterns
- `MockSentimentAnalyst`: Returns social/market sentiment analysis
- `MockMacroNewsAnalyst`: Returns macro economic analysis

### Strategy & Research Team (3 agents)
- `MockBullishResearcher`: Returns bullish debate arguments
- `MockBearishResearcher`: Returns bearish debate arguments
- `MockDerivativesStrategist`: Returns F&O strategy proposals

### Execution Team (2 agents)
- `MockEquityTrader`: Returns equity execution plans
- `MockFnOTrader`: Returns options execution plans

### Oversight Team (3 agents)
- `MockRiskManager` (CriticalAgent): Returns risk assessments
- `MockPortfolioManager` (CriticalAgent): Returns final decisions
- `MockReflectiveAgent` (CriticalAgent): Returns trade reflections

## Usage Examples

### Basic Usage

```python
from tests.mock_agents import MockFundamentalsAnalyst

async def test_my_workflow():
    agent = MockFundamentalsAnalyst()
    report = await agent.analyze({"symbol": "AAPL"})
    
    assert report.symbol == "AAPL"
    assert report.confidence > 0.5
```

### Using Fixtures

```python
@pytest.mark.asyncio
async def test_with_fixture(mock_fundamentals_analyst, sample_context):
    report = await mock_fundamentals_analyst.analyze(sample_context)
    assert isinstance(report, FundamentalsReport)
```

### Testing Complete Workflows

```python
@pytest.mark.asyncio
async def test_analysis_phase(
    mock_fundamentals_analyst,
    mock_technical_analyst,
    mock_sentiment_analyst,
    mock_macro_news_analyst,
    sample_context
):
    # Run all market intelligence agents
    reports = await asyncio.gather(
        mock_fundamentals_analyst.analyze(sample_context),
        mock_technical_analyst.analyze(sample_context),
        mock_sentiment_analyst.analyze(sample_context),
        mock_macro_news_analyst.analyze(sample_context),
    )
    
    # Verify all completed successfully
    assert len(reports) == 4
    assert all(r.symbol == sample_context["symbol"] for r in reports)
```

### Controlling Mock Behavior

Some mocks support behavioral control:

```python
@pytest.mark.asyncio
async def test_risk_rejection():
    agent = MockRiskManager()
    
    # Force rejection
    context = {"symbol": "AAPL", "should_approve": False}
    assessment = await agent.assess_risk(context)
    
    assert assessment.approved is False
```

## Available Fixtures

All mock agents are available as pytest fixtures (see `tests/conftest.py`):

- `mock_fundamentals_analyst`
- `mock_technical_analyst`
- `mock_sentiment_analyst`
- `mock_macro_news_analyst`
- `mock_bullish_researcher`
- `mock_bearish_researcher`
- `mock_derivatives_strategist`
- `mock_equity_trader`
- `mock_fno_trader`
- `mock_risk_manager`
- `mock_portfolio_manager`
- `mock_reflective_agent`

## Test Coverage

### Current Test Files

1. **test_agents_market_intelligence.py** (25 tests)
   - Tests all 4 Market Intelligence agents
   - Validates report structures
   - Tests metadata and timestamps
   - Integration tests

2. **test_agents_strategy_research.py** (24 tests)
   - Tests debate functionality
   - Tests strategy proposals
   - Tests multi-round debates
   - Workflow integration

3. **test_agents_execution.py** (25 tests)
   - Tests execution plan generation
   - Validates order structures
   - Tests cost estimation
   - Tests both equity and options

4. **test_agents_oversight.py** (31 tests)
   - Tests risk assessments
   - Tests portfolio decisions
   - Tests reflection capabilities
   - Tests approval workflows

### Coverage Metrics

```bash
# Run all agent mock tests
pytest tests/test_agents_*.py -v

# Check coverage for agent modules
pytest tests/test_agents_*.py --cov=src/agents --cov-report=html

# Run specific test file
pytest tests/test_agents_market_intelligence.py -v
```

## Swapping Real and Mock Agents

### Method 1: Direct Substitution

```python
# Production
from src.agents.market_intelligence import FundamentalsAnalyst

# Testing
from tests.mock_agents import MockFundamentalsAnalyst as FundamentalsAnalyst
```

### Method 2: Fixture Override

```python
@pytest.fixture
def fundamentals_analyst(use_mock=True):
    if use_mock:
        from tests.mock_agents import MockFundamentalsAnalyst
        return MockFundamentalsAnalyst()
    else:
        from src.agents.market_intelligence import FundamentalsAnalyst
        return FundamentalsAnalyst()
```

### Method 3: Configuration-Based

```python
# In workflow code
def get_agent(agent_type, use_mock=False):
    if use_mock:
        return get_mock_agent(agent_type)
    else:
        return get_real_agent(agent_type)
```

## Performance Benchmarks

Mock agents are designed for speed:

```
MockFundamentalsAnalyst.analyze():  < 0.001s
MockTechnicalAnalyst.analyze():     < 0.001s
MockSentimentAnalyst.analyze():     < 0.001s
MockMacroNewsAnalyst.analyze():     < 0.001s

Complete workflow (12 agents):      < 0.1s
```

Compare to real agents (with API calls):
```
Real agent with LLM call:           2-5s per agent
Complete workflow (12 agents):      30-60s
```

## Data Schemas

All mock agents return proper Pydantic models that match real agent outputs:

- `FundamentalsReport`: PE ratio, intrinsic value, investment thesis
- `TechnicalReport`: Support/resistance, trend direction, chart patterns
- `SentimentReport`: Sentiment score, volume trends, retail interest
- `MacroNewsReport`: Key events, economic indicators, geopolitical risks
- `DebateArgument`: Arguments with supporting evidence
- `StrategyProposal`: Strategy type, risk/reward, entry/exit criteria
- `ExecutionPlan`: Orders, cost estimates, timing recommendations
- `RiskAssessment`: VaR, position sizing, sector exposure
- `PortfolioDecision`: Approval status, monitoring requirements

## Best Practices

1. **Use Mock Agents for Unit Tests**: Test individual components quickly
2. **Use Real Agents for Integration Tests**: Test actual LLM interactions (expensive)
3. **Always Use Fixtures**: Promotes consistency and reusability
4. **Test Both Scenarios**: Mock for speed, real for accuracy
5. **Mock Data Providers Too**: Avoid network calls in tests

## Extending Mock Agents

To add new mock agents:

1. Create class inheriting from `MockBaseAgent` or `MockCriticalAgent`
2. Implement required methods with deterministic data
3. Add fixture to `conftest.py`
4. Create test file with comprehensive tests

Example:

```python
class MockNewAgent(MockBaseAgent):
    def __init__(self):
        super().__init__(
            role=AgentRole.NEW_AGENT,
            system_prompt="Mock new agent",
            temperature=0.7,
        )
    
    async def analyze(self, context: dict[str, Any]) -> AgentReport:
        return AgentReport(
            agent_role=self.role,
            symbol=context.get("symbol", "TEST"),
            summary="Mock analysis",
            confidence=0.8,
        )
```

## CI/CD Integration

Mock agents enable fast, reliable CI/CD:

```yaml
# .github/workflows/test.yml
- name: Run Agent Tests
  run: |
    pytest tests/test_agents_*.py \
      --cov=src/agents \
      --cov-fail-under=80 \
      --maxfail=1
```

No API keys required in CI environment!

## Troubleshooting

### ImportError for agents
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check Python path includes project root

### Tests failing unexpectedly
- Verify fixtures are loaded: `pytest --fixtures`
- Check mock data matches expected schemas
- Ensure async functions use `@pytest.mark.asyncio`

### Coverage not increasing
- Mock agents test mock code, not real agents
- For real agent coverage, mock LLM at agent level
- See `test_agent_base.py` for examples

## Summary

The mock agent system provides:
- ✅ 12 mock agent implementations
- ✅ 105 comprehensive tests
- ✅ <5s total test execution time
- ✅ No API dependencies
- ✅ Easy integration via fixtures
- ✅ Full Pydantic schema compliance
- ✅ CI/CD ready

This enables fast, reliable testing of agent workflows without the cost and latency of real LLM API calls.
