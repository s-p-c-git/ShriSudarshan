# Contributing to Project Shri Sudarshan

Thank you for your interest in contributing to Project Shri Sudarshan! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Areas for Contribution](#areas-for-contribution)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Expected Behavior

- Be respectful and professional
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Publishing others' private information
- Trolling or insulting comments
- Other unprofessional conduct

---

## Getting Started

### Prerequisites

1. **Python 3.9+** installed
2. **Git** for version control
3. **OpenAI API key** for testing agents
4. Familiarity with:
   - Python async/await
   - Pydantic for data validation
   - LangGraph for orchestration (helpful but not required)

### Setup Development Environment

1. **Fork the repository**:
   - Go to https://github.com/s-p-c-git/ShriSudarshan
   - Click "Fork" button

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ShriSudarshan.git
   cd ShriSudarshan
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/s-p-c-git/ShriSudarshan.git
   ```

4. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

6. **Install development tools**:
   ```bash
   pip install black ruff mypy pytest pytest-asyncio pytest-cov
   ```

7. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (for testing)
   ```

8. **Run tests** to verify setup:
   ```bash
   pytest tests/
   ```

---

## Development Workflow

### Creating a Feature Branch

1. **Update your fork**:
   ```bash
   git checkout main
   git fetch upstream
   git merge upstream/main
   ```

2. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

   Branch naming conventions:
   - `feature/` - New features
   - `fix/` - Bug fixes
   - `docs/` - Documentation changes
   - `refactor/` - Code refactoring
   - `test/` - Test additions/improvements

### Making Changes

1. **Write code** following [coding standards](#coding-standards)

2. **Write tests** for new functionality

3. **Run tests locally**:
   ```bash
   pytest tests/
   ```

4. **Format code**:
   ```bash
   black src/ tests/
   ```

5. **Lint code**:
   ```bash
   ruff check src/ tests/
   ```

6. **Type check**:
   ```bash
   mypy src/
   ```

7. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

   Commit message format:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation
   - `test:` - Test changes
   - `refactor:` - Code refactoring
   - `chore:` - Maintenance tasks

---

## Coding Standards

### Python Style

Follow **PEP 8** standards with these specifics:

#### Line Length
- **Maximum 100 characters** (flexible to 120 for readability)
- Break long lines logically

#### Indentation
- **4 spaces** (never tabs)
- Continuation lines should be indented

#### Imports
```python
# Standard library imports
import os
from datetime import datetime

# Third-party imports
import pandas as pd
from pydantic import BaseModel

# Local imports
from ..config import settings
from ..data.schemas import AgentRole
```

#### Type Hints

Always use type hints:

```python
def analyze_data(
    symbol: str,
    period: int = 30,
    detailed: bool = False
) -> Dict[str, Any]:
    """Analyze data for the given symbol."""
    pass
```

#### Docstrings

Use **Google-style docstrings**:

```python
def calculate_metrics(
    prices: pd.DataFrame,
    window: int = 20
) -> Dict[str, float]:
    """
    Calculate technical metrics from price data.
    
    Args:
        prices: DataFrame with OHLCV data
        window: Rolling window size for calculations
        
    Returns:
        Dict with calculated metrics
        
    Raises:
        ValueError: If prices DataFrame is empty
        
    Example:
        >>> prices = get_price_history("AAPL")
        >>> metrics = calculate_metrics(prices, window=20)
        >>> print(metrics['sma'])
    """
    pass
```

#### Naming Conventions

- **Classes**: PascalCase (`BaseAgent`, `MarketDataProvider`)
- **Functions/Methods**: snake_case (`analyze`, `get_current_price`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_POSITION_SIZE`)
- **Private**: Prefix with underscore (`_generate_response`, `_cache`)

#### Error Handling

```python
try:
    result = await api_call()
except SpecificException as e:
    logger.error("Operation failed", error=str(e))
    # Handle error gracefully
    return default_value
```

- Catch specific exceptions (not bare `except:`)
- Log errors with context
- Provide sensible defaults
- Don't silence errors without logging

### Async/Await

- Use `async def` for I/O-bound operations
- Use `await` for async calls
- Use `asyncio.gather()` for concurrent operations

```python
async def run_analysts(context):
    results = await asyncio.gather(
        fundamentals_agent.analyze(context),
        technical_agent.analyze(context),
        return_exceptions=True
    )
    return results
```

### Data Validation

Use Pydantic for all data structures:

```python
from pydantic import BaseModel, Field

class AgentReport(BaseModel):
    symbol: str
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True
```

---

## Testing Guidelines

### Test Structure

Place tests in `tests/` directory mirroring `src/`:

```
tests/
├── test_agents/
│   ├── test_fundamentals_analyst.py
│   └── test_technical_analyst.py
├── test_data/
│   ├── test_schemas.py
│   └── test_providers.py
└── test_orchestration/
    └── test_workflow.py
```

### Writing Tests

Use `pytest` framework:

```python
import pytest
from src.agents import FundamentalsAnalyst

class TestFundamentalsAnalyst:
    """Test suite for FundamentalsAnalyst."""
    
    def test_initialization(self):
        """Test agent initializes correctly."""
        agent = FundamentalsAnalyst()
        assert agent.role == AgentRole.FUNDAMENTALS_ANALYST
    
    @pytest.mark.asyncio
    async def test_analyze(self, sample_context):
        """Test analysis with valid context."""
        agent = FundamentalsAnalyst()
        report = await agent.analyze(sample_context)
        
        assert report.symbol == sample_context["symbol"]
        assert 0 <= report.confidence <= 1.0
```

### Test Fixtures

Define reusable fixtures in `tests/conftest.py`:

```python
import pytest

@pytest.fixture
def sample_context():
    """Provide sample analysis context."""
    return {
        "symbol": "AAPL",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
    }
```

### Mocking External APIs

Mock external calls to avoid API costs and rate limits:

```python
from unittest.mock import Mock, patch

@patch('src.data.providers.market_data.yf.Ticker')
def test_get_fundamentals(mock_ticker):
    """Test fundamentals fetching."""
    mock_instance = Mock()
    mock_instance.info = {'pe_ratio': 28.5, 'symbol': 'AAPL'}
    mock_ticker.return_value = mock_instance
    
    provider = MarketDataProvider()
    fundamentals = provider.get_fundamentals("AAPL")
    
    assert fundamentals['pe_ratio'] == 28.5
```

### Test Coverage

- Minimum coverage: **50%** (defined in pytest.ini)
- Aim for **80%+** for new code
- Run coverage report:
  ```bash
  pytest --cov=src tests/
  ```

### Testing Async Code

Use `pytest-asyncio`:

```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async functionality."""
    result = await some_async_function()
    assert result is not None
```

---

## Pull Request Process

### Before Submitting

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Run full test suite**:
   ```bash
   pytest tests/
   ```

4. **Format and lint code**:
   ```bash
   black src/ tests/
   ruff check src/ tests/
   mypy src/
   ```

5. **Update CHANGELOG** (if applicable)

6. **Rebase on latest main**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

### Creating Pull Request

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open pull request** on GitHub

3. **Fill out PR template**:
   - Description of changes
   - Motivation and context
   - Type of change (feature, fix, docs, etc.)
   - Testing done
   - Related issues

4. **Link related issues**:
   ```
   Closes #123
   Fixes #456
   ```

### PR Title Format

```
<type>: <description>

Examples:
feat: Add derivatives strategist agent
fix: Correct sentiment score calculation
docs: Update API reference for new schemas
test: Add tests for risk manager
```

### Review Process

1. **Automated checks** will run:
   - Tests
   - Linting
   - Type checking
   - Coverage

2. **Maintainer review**:
   - Code quality
   - Test coverage
   - Documentation
   - Adherence to standards

3. **Address feedback**:
   - Make requested changes
   - Push updates to same branch
   - PR updates automatically

4. **Approval and merge**:
   - Maintainer will merge when ready
   - Squash merge for clean history

---

## Areas for Contribution

### High Priority

1. **Testing**:
   - Unit tests for agents
   - Integration tests for workflow
   - End-to-end tests
   - Load/performance tests

2. **Data Providers**:
   - Additional news sources
   - Options data providers (alternatives to yfinance)
   - Economic calendar API integration
   - Real-time data feeds

3. **Agent Improvements**:
   - Enhanced LLM prompts
   - Better confidence scoring
   - Advanced analysis techniques
   - Multi-turn debate improvements

4. **Risk Management**:
   - Advanced VaR calculations
   - Stress testing scenarios
   - Position correlation analysis
   - Dynamic risk limits

### Medium Priority

1. **Backtesting**:
   - Historical simulation framework
   - Performance analytics
   - Strategy comparison tools
   - Walk-forward optimization

2. **Broker Integration**:
   - Interactive Brokers API
   - Alpaca API
   - Other broker connectors
   - Paper trading improvements

3. **UI/Dashboard**:
   - Web-based monitoring dashboard
   - Real-time agent status
   - Trade visualization
   - Performance charts

4. **Documentation**:
   - Video tutorials
   - More examples
   - Best practices guide
   - Agent customization guide

### Low Priority (Future)

1. **Machine Learning**:
   - Pattern recognition models
   - Reinforcement learning for strategy optimization
   - Sentiment models (beyond keywords)
   - Price prediction models

2. **Advanced Features**:
   - Multi-asset portfolio management
   - Sector rotation strategies
   - Market regime detection
   - Automated rebalancing

3. **Scalability**:
   - Distributed execution
   - Database optimization
   - Caching layers
   - Message queues

---

## Communication

### GitHub Issues

- **Bug reports**: Use bug report template
- **Feature requests**: Use feature request template
- **Questions**: Use discussion forum or Q&A template

### Discussions

Use GitHub Discussions for:
- Questions about usage
- Architecture discussions
- Feature brainstorming
- Sharing experiences

### Response Time

- Maintainers typically respond within 1-3 days
- Complex PRs may take longer to review
- Please be patient!

---

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in commit history

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

## Questions?

- **Documentation**: See [Getting Started](getting_started.md), [Architecture](architecture.md)
- **Issues**: https://github.com/s-p-c-git/ShriSudarshan/issues
- **Discussions**: https://github.com/s-p-c-git/ShriSudarshan/discussions

---

Thank you for contributing to Project Shri Sudarshan! 🚀
