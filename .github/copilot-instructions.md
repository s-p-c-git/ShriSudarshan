# GitHub Copilot Instructions - Project Shri Sudarshan

## Project Overview

Project Shri Sudarshan is a hybrid multi-agent LLM architecture for stock and derivatives trading. The system uses LangGraph to orchestrate 11 specialized agents across 4 teams (Market Intelligence, Strategy & Research, Execution, and Oversight & Learning) to analyze markets, debate strategies, manage risk, and execute trades.

## Core Architecture Principles

- **Multi-Agent System**: 11 specialized LLM agents work collaboratively
- **Team-Based Structure**: 4 distinct teams (Market Intelligence, Strategy & Research, Execution, Oversight & Learning)
- **LangGraph Orchestration**: State management and workflow control
- **Three-Layer Memory**: Working memory (current state), Procedural memory (workflows), Episodic memory (historical trades)
- **Hierarchical Decision Making**: Analysis → Debate → Risk Check → Approval → Execution
- **Reflective Learning**: Post-trade analysis feeds back into strategy refinement

## Coding Style & Conventions

### Python Style Guidelines

- **Python Version**: Python 3.9+ with modern type hints
- **Formatting**: Follow PEP 8 standards
- **Indentation**: 4 spaces (not tabs)
- **Line Length**: Maximum 100 characters (flexible to 120 for readability)
- **Imports**: 
  - Standard library imports first
  - Third-party imports second
  - Local imports last
  - Use absolute imports from `src` root

### Docstring Standards

- Use Google-style docstrings for all public functions, classes, and methods
- Include type hints in function signatures, not in docstrings
- Document all parameters, return values, and exceptions
- Example:
```python
def analyze(self, context: Dict[str, Any]) -> AgentReport:
    """
    Perform analysis based on the given context.
    
    Args:
        context: Dictionary containing analysis context (symbol, data, etc.)
        
    Returns:
        AgentReport: Structured report from the agent
        
    Raises:
        ValueError: If required context fields are missing
    """
```

### Type Hints

- Always use type hints for function parameters and return values
- Use `Optional[Type]` for nullable values
- Use `Dict[str, Any]` for flexible dictionaries
- Use `from typing import` imports at module level

### Naming Conventions

- **Classes**: PascalCase (e.g., `BaseAgent`, `FundamentalsAnalyst`)
- **Functions/Methods**: snake_case (e.g., `analyze`, `get_metadata`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_POSITION_SIZE`)
- **Private Methods**: Prefix with underscore (e.g., `_generate_response`)
- **Protected Members**: Single underscore prefix

## Project Structure

```
src/
├── agents/              # Agent implementations
│   ├── base.py         # BaseAgent and CriticalAgent classes
│   ├── market_intelligence/  # Analysis agents
│   ├── strategy_research/    # Debate agents
│   ├── execution/            # Trading agents
│   └── oversight/            # Management agents
├── config/             # Configuration and prompts
│   ├── settings.py     # Pydantic settings management
│   └── prompts.py      # System prompts for agents
├── memory/             # Memory system
│   ├── working.py      # Short-term state
│   ├── procedural.py   # Workflow patterns
│   └── episodic.py     # Historical trades
├── orchestration/      # LangGraph workflow
│   ├── workflow.py     # Main workflow orchestration
│   └── state.py        # State definitions
├── data/               # Data models and schemas
├── utils/              # Utility functions
│   └── logger.py       # Structured logging
└── main.py             # CLI entry point
```

## Agent Development Guidelines

### Creating New Agents

1. Inherit from `BaseAgent` or `CriticalAgent` (for management-level agents)
2. Define the agent's `AgentRole` enum value
3. Implement the `analyze()` method
4. Use system prompts from `config/prompts.py`
5. Return structured `AgentReport` objects

### Agent Types

- **BaseAgent**: Standard agents using `gpt-4o-mini` (analysis, research)
- **CriticalAgent**: Premium agents using `gpt-4o` (portfolio manager, risk manager)

### LLM Usage Guidelines

- Use async methods (`ainvoke`) for LLM calls
- Handle rate limits and retries appropriately
- Set appropriate temperature values (0.7 default, lower for deterministic outputs)
- Keep prompts focused and structured
- Include relevant context but avoid excessive token usage

## Memory System

### Working Memory
- Uses in-memory dictionary for current analysis state
- Cleared after each workflow run
- Stores intermediate results between phases

### Procedural Memory
- Stores successful workflow patterns
- Uses ChromaDB (version 0.4.0+) for vector storage
- Helps optimize agent task execution

### Episodic Memory
- SQLAlchemy ORM for trade records
- Stores complete trade history with rationale
- Used by Reflective Agent for learning

## Configuration Management

- Use `pydantic-settings` for all configuration
- Load from `.env` file (never commit `.env` files)
- Validate configuration at startup
- Provide sensible defaults in `config/settings.py`
- All API keys and secrets go in environment variables

### Key Configuration Areas

- **LLM Settings**: API keys, model names, temperature
- **Data Providers**: Alpha Vantage, Tradier, etc.
- **Risk Parameters**: Position limits, VaR thresholds
- **Memory**: Database URLs, cache settings
- **Execution**: Paper trading vs live trading flags

## Testing Guidelines

### Test Framework

- Use `pytest` for all tests
- Use `pytest-asyncio` for async tests
- Use `pytest-cov` for coverage tracking
- Minimum coverage target: 50% (defined in `pytest.ini`)

### Test Structure

- Place tests in `tests/` directory mirroring `src/` structure
- Name test files `test_<module>.py`
- Name test functions `test_<functionality>`
- Use fixtures from `tests/conftest.py`

### Test Patterns

```python
@pytest.mark.asyncio
async def test_agent_analysis(sample_context):
    """Test agent analysis with sample data."""
    agent = FundamentalsAnalyst()
    report = await agent.analyze(sample_context)
    
    assert report.role == AgentRole.FUNDAMENTALS_ANALYST
    assert report.analysis is not None
    assert report.confidence >= 0.0 and report.confidence <= 1.0
```

### Mocking

- Mock external API calls (OpenAI, data providers)
- Use fixtures for common test data
- Mock time-dependent operations

## Security Best Practices

### API Keys & Secrets

- **Never** hardcode API keys or secrets in code
- Use environment variables loaded from `.env`
- Add `.env` to `.gitignore` (already configured)
- Provide `.env.example` template without sensitive data
- Validate API keys exist before use

### Data Handling

- Sanitize all external input before processing
- Use parameterized queries for database operations (SQLAlchemy handles this)
- Validate financial data before making decisions
- Log security-relevant events

### Risk Management

- Enforce position size limits
- Implement circuit breakers for excessive losses
- Require explicit confirmation for live trading
- Default to paper trading mode
- Validate all trade parameters before execution

## Error Handling

### Best Practices

- Use try-except blocks for external API calls
- Catch specific exceptions, not bare `except:`
- Log errors with context using structured logging
- Provide helpful error messages to users
- Implement graceful degradation where possible

### Logging

- Use `structlog` for structured logging
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Include context in log messages (symbol, phase, agent role)
- Use logger from `utils.logger` module
- Example:
```python
logger.info("Starting analysis", symbol=symbol, agent=self.role.value)
```

## Async/Await Patterns

- Use `async def` for I/O-bound operations (LLM calls, API requests)
- Use `await` for async function calls
- Use `asyncio.gather()` for concurrent operations
- Handle exceptions in concurrent tasks properly
- Example:
```python
async def run_analysis_phase(context):
    results = await asyncio.gather(
        fundamentals_agent.analyze(context),
        technical_agent.analyze(context),
        sentiment_agent.analyze(context),
        return_exceptions=True
    )
    return results
```

## Data Providers & External APIs

### Supported Providers

- **yfinance**: Stock price data, historical data (currently implemented)
- **Alpha Vantage**: Fundamentals, news (API key optional, see `.env.example`)
- **Tradier**: Options data, Greeks (planned for future implementation, API key configuration available)

### API Call Guidelines

- Cache responses when appropriate
- Implement rate limiting
- Handle API errors gracefully
- Provide fallback data sources
- Respect provider rate limits

## LangGraph Workflow

### State Management

- Define state in `orchestration/state.py`
- Use TypedDict for state structure
- Update state immutably (return new state)
- Validate state transitions

### Workflow Phases

1. **Analysis Phase**: Market Intelligence team runs concurrently
2. **Debate Phase**: Bull/Bear researchers debate
3. **Strategy Phase**: Derivatives strategist proposes FnO strategies
4. **Risk Check**: Risk Manager validates proposal
5. **Approval**: Portfolio Manager makes final decision
6. **Execution**: Trader agents execute approved trades
7. **Reflection**: Post-trade learning loop

### Adding New Workflow Nodes

- Define node function with state parameter
- Update state with results
- Add node to workflow graph
- Define transitions and conditions

## Financial Domain Guidelines

### Options & Derivatives

- Understand Greeks (Delta, Gamma, Theta, Vega)
- Calculate implied volatility vs historical volatility
- Consider expiration dates and time decay
- Validate multi-leg strategy feasibility

### Risk Metrics

- Calculate Value at Risk (VaR)
- Monitor sector concentration
- Track portfolio beta
- Implement stop-loss mechanisms

### Market Analysis

- Combine fundamental, technical, and sentiment analysis
- Consider macro conditions and news events
- Validate data quality and timeliness
- Handle market hours and holidays

## Development Workflow

### Getting Started

1. Clone repository
2. Copy `.env.example` to `.env` and add API keys
3. Install dependencies: `pip install -r requirements.txt`
4. Run tests: `pytest`
5. Run linting: `ruff check src/` and `black --check src/`
6. Run the system: `cd src && python main.py --symbol AAPL`

### Code Quality Tools

- **black**: Code formatting (run before commit)
- **ruff**: Fast Python linter (check for issues)
- **mypy**: Static type checking
- **pytest**: Testing framework

### Before Committing

1. Run formatters: `black src/ tests/`
2. Run linters: `ruff check src/ tests/`
3. Run type checker: `mypy src/`
4. Run tests: `pytest`
5. Ensure coverage meets minimum: 50%

## Documentation

### Code Documentation

- Document all public APIs with docstrings
- Keep docstrings up-to-date with code changes
- Include examples in docstrings for complex functions
- Document assumptions and limitations

### Project Documentation

- **README.md**: High-level overview and quick start
- **APPROACH.md**: Detailed architecture and implementation approach
- **IMPLEMENTATION_SUMMARY.md**: Current implementation status
- **docs/architecture.md**: System architecture details
- **docs/getting_started.md**: Detailed installation and usage guide

### Documentation Updates

- Update documentation when changing public APIs
- Update implementation status when completing features
- Keep examples current and working
- Document breaking changes clearly

## Performance Considerations

- Minimize LLM token usage (costs money)
- Cache expensive computations
- Use concurrent execution for independent operations
- Monitor memory usage for large datasets
- Optimize database queries

## Common Pitfalls to Avoid

- Don't commit `.env` files or API keys
- Don't use `print()` for logging (use `logger`)
- Don't make synchronous LLM calls (use `ainvoke`)
- Don't ignore error handling for external APIs
- Don't create agents without proper base class inheritance
- Don't bypass risk checks or approval gates
- Don't test with real money (use paper trading)
- Don't remove or modify working memory after execution
- Don't hardcode file paths (use Path from pathlib)

## When Adding New Features

1. Review existing architecture patterns
2. Follow the multi-agent design principles
3. Add configuration options to settings
4. Write tests before implementation
5. Update documentation
6. Ensure backward compatibility
7. Consider impact on existing workflows
8. Test in paper trading mode first

## Questions or Clarifications

If you need clarification on:
- Architecture decisions: See `APPROACH.md` and `docs/architecture.md`
- Current implementation status: See `IMPLEMENTATION_SUMMARY.md`
- Usage examples: See `docs/getting_started.md` and `examples/`
- Testing: See `tests/conftest.py` for fixtures and patterns

## Additional Resources

- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/
- **LangChain Documentation**: https://python.langchain.com/
- **OpenAI API Reference**: https://platform.openai.com/docs/
- **Trading Concepts**: Financial domain knowledge required for understanding agent logic

---

Remember: This is a financial trading system. Code quality, security, and risk management are paramount. Always default to safety and paper trading mode.
