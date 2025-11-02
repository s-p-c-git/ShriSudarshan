# Test Suite Documentation

## Overview

This document describes the comprehensive test suite for Project Shri Sudarshan Phase 2, covering unit tests, integration tests, and functional tests for all system components.

## Test Structure

```
tests/
├── conftest.py                      # Shared fixtures and test configuration
├── test_data_schemas.py             # Data schema validation tests
├── test_data_providers_market.py    # Market data provider tests
├── test_data_providers_news.py      # News provider tests
├── test_memory_working.py           # Working memory tests
├── test_memory_procedural.py        # Procedural memory tests
├── test_memory_episodic.py          # Episodic memory tests
├── test_orchestration_state.py      # Workflow state tests
└── test_functional_workflow.py      # End-to-end integration tests
```

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install pytest pytest-asyncio pytest-cov
```

### Run All Tests

```bash
cd /path/to/ShriSudarshan
pytest
```

### Run Specific Test Files

```bash
# Run memory tests
pytest tests/test_memory_working.py

# Run data provider tests
pytest tests/test_data_providers_market.py

# Run with verbose output
pytest -v tests/test_data_schemas.py
```

### Run With Coverage

```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing

# View HTML coverage report
# Open htmlcov/index.html in browser
```

### Run Specific Test Classes or Methods

```bash
# Run specific test class
pytest tests/test_memory_working.py::TestWorkingMemory

# Run specific test method
pytest tests/test_memory_working.py::TestWorkingMemory::test_set_and_get
```

### Skip Integration Tests

Integration tests that require network access are marked with `@pytest.mark.skip`:

```bash
# Run only unit tests (skip integration)
pytest -v  # Integration tests are already skipped by default
```

## Test Coverage

### Unit Tests

#### Data Layer (Complete ✅)
- **test_data_schemas.py** (150+ tests)
  - All Pydantic model validation
  - Enum definitions
  - Field constraints and defaults
  - Complex nested models

- **test_data_providers_market.py** (25+ tests)
  - Price history retrieval
  - Fundamental data fetching
  - Technical indicator calculation
  - Options chain data
  - Error handling and fallbacks
  - Comprehensive mocking

- **test_data_providers_news.py** (30+ tests)
  - Company news retrieval
  - Market news aggregation
  - Sentiment analysis (keyword-based)
  - Economic calendar
  - Deduplication logic

#### Memory Layer (Complete ✅)
- **test_memory_working.py** (25+ tests)
  - TTL-based expiration
  - CRUD operations
  - Cleanup mechanisms
  - Complex data types
  - Concurrent access

- **test_memory_episodic.py** (30+ tests)
  - Trade outcome storage
  - Reflection storage
  - SQL database operations
  - Performance statistics
  - Multi-symbol queries

- **test_memory_procedural.py** (15+ tests)
  - Pattern storage (ChromaDB)
  - Similarity search
  - Mock mode fallback
  - Pattern retrieval and deletion

#### Orchestration Layer (Complete ✅)
- **test_orchestration_state.py** (30+ tests)
  - State initialization
  - Phase transitions
  - Error tracking
  - Approval gates
  - State mutation

### Functional Tests (Partial ✅)
- **test_functional_workflow.py** (10+ tests)
  - Workflow state structure
  - Memory integration
  - Data provider integration
  - End-to-end flows (marked for manual testing)

### Test Statistics

- **Total Test Files**: 9
- **Total Test Classes**: 35+
- **Total Test Functions**: 250+
- **Code Coverage Target**: 50%+ (as per pytest.ini)

## Test Fixtures

### Basic Fixtures (conftest.py)

- `sample_symbol`: Stock symbol for testing ("AAPL")
- `sample_symbols`: Multiple stock symbols
- `sample_date_range`: Date range for historical data

### Data Fixtures

- `sample_price_history`: Pandas DataFrame with OHLCV data
- `sample_fundamentals`: Fundamental metrics dictionary
- `sample_technical_indicators`: Technical indicators dictionary
- `sample_news_articles`: List of news article dictionaries

### Report Fixtures

- `sample_fundamentals_report`: FundamentalsReport instance
- `sample_macro_news_report`: MacroNewsReport instance
- `sample_sentiment_report`: SentimentReport instance
- `sample_technical_report`: TechnicalReport instance
- `sample_analyst_reports`: Complete set of reports

### Strategy Fixtures

- `sample_debate_arguments`: List of DebateArgument instances
- `sample_strategy_proposal`: StrategyProposal instance
- `sample_execution_plan`: ExecutionPlan with orders
- `sample_risk_assessment`: RiskAssessment instance
- `sample_portfolio_decision`: PortfolioDecision instance

### Mock Fixtures

- `mock_market_data_provider`: Mocked MarketDataProvider
- `mock_news_provider`: Mocked NewsProvider
- `mock_llm`: Mocked LLM for agent testing

### Context Fixtures

- `sample_context`: Complete context for agent testing
- `sample_workflow_state`: Workflow state dictionary
- `test_env_vars`: Test environment variables

## Test Categories

### Fast Unit Tests
Tests that run quickly without external dependencies:
- Schema validation
- Memory operations (working memory)
- State management
- Pure logic tests

### Slow Unit Tests
Tests that involve I/O or heavier operations:
- Database operations (episodic memory)
- Vector database operations (procedural memory)
- File system operations

### Integration Tests
Tests marked with `@pytest.mark.skip` that require:
- Network access (real API calls)
- LLM API keys
- Complete system setup

## Mocking Strategy

### External APIs
All external API calls are mocked using `unittest.mock`:
- **yfinance**: Market data provider mocked to avoid network calls
- **OpenAI API**: LLM responses mocked for agent testing
- **ChromaDB**: Can operate in mock mode when unavailable

### Benefits
- Tests run fast without network dependency
- Deterministic test results
- No API rate limits or costs
- Can test error scenarios

## Test Data

### Sample Data Characteristics
- **Realistic Values**: Test data uses realistic price ranges and metrics
- **Edge Cases**: Tests include boundary conditions and edge cases
- **Error Scenarios**: Tests cover error handling and fallbacks
- **Time-based Data**: Proper datetime handling and timezone awareness

## Continuous Integration

### pytest.ini Configuration
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto

# Minimum coverage requirement
addopts = 
    --verbose
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=50
```

### Running in CI/CD
```bash
# In CI pipeline
pytest --cov=src --cov-report=xml --cov-fail-under=50
```

## Known Limitations

### Network-Dependent Tests
Some integration tests are skipped by default because they require:
- Active internet connection
- Valid API keys
- External service availability

To run these tests:
1. Set up environment variables (OPENAI_API_KEY, etc.)
2. Remove `@pytest.mark.skip` decorator
3. Run with network access

### Agent Tests
Full agent testing requires:
- LLM API access
- Valid responses from LLM
- Higher test execution time

These are candidates for integration test suites.

## Future Enhancements

### Planned Test Additions
1. **Agent Unit Tests**: Test individual agent implementations
2. **Workflow Tests**: Complete workflow execution tests
3. **Performance Tests**: Load and stress testing
4. **Security Tests**: Input validation and security checks
5. **UI Tests**: If web interface is added

### Coverage Goals
- Increase code coverage to 80%+
- Add property-based testing with Hypothesis
- Add mutation testing for test quality
- Add benchmarking tests

## Troubleshooting

### Common Issues

#### ChromaDB Not Available
If ChromaDB is not installed:
- Procedural memory tests will use mock mode
- Tests will still pass but with reduced functionality

#### Database Lock Errors
If you see database lock errors:
- Close any SQLite browser connections
- Use temporary databases for each test

#### Async Test Failures
If async tests fail:
- Ensure pytest-asyncio is installed
- Check asyncio_mode in pytest.ini

#### Import Errors
If modules can't be imported:
- Ensure you're running pytest from project root
- Check PYTHONPATH includes src directory

### Getting Help

For issues with tests:
1. Check test output for specific error messages
2. Run with `-v` flag for verbose output
3. Run specific failing test in isolation
4. Check conftest.py for fixture definitions

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure tests pass locally
3. Maintain >50% code coverage
4. Add fixtures to conftest.py if reusable
5. Document complex test scenarios
6. Mock external dependencies

## References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
