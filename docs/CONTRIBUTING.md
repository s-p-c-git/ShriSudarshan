# Contributing to Project Shri Sudarshan

Thank you for your interest in contributing to Project Shri Sudarshan! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [⚠️ **Important: Code Formatting Requirements**](#important-code-formatting-requirements)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Areas for Contribution](#areas-for-contribution)

---

## ⚠️ **Important: Code Formatting Requirements**

**ALL CODE MUST BE FORMATTED BEFORE COMMITTING!** This is enforced by CI/CD and will block your PR from merging.

### Required Setup (Do This First!)

**Step 1:** Install development tools:
```bash
pip install black ruff mypy pytest pytest-asyncio pytest-cov pre-commit
```

**Step 2:** Install pre-commit hooks (MANDATORY):
```bash
pre-commit install
```

This will automatically format your code with Black and organize imports with Ruff on every commit.

### Manual Formatting (If Needed)

If you need to format code manually or if CI fails:

```bash
# Format all code with Black
black src/ tests/ examples/

# Fix import organization and other issues with Ruff
ruff check --fix src/ tests/ examples/

# Verify formatting is correct
black --check src/ tests/ examples/
ruff check src/ tests/ examples/
```

### Why This Matters

- **CI/CD will FAIL** if code is not properly formatted
- **PRs cannot be merged** without passing formatting checks
- Formatting prevents recurring issues and maintains code quality
- Pre-commit hooks save time by catching issues before CI/CD

### For AI/Copilot Generated Code

All AI-generated or modified code must also be formatted:
1. After generating code, always run: `black src/ tests/ examples/`
2. Then run: `ruff check --fix src/ tests/ examples/`
3. Commit the formatted code

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

6. **Install development tools (REQUIRED)**:
   ```bash
   pip install black ruff mypy pytest pytest-asyncio pytest-cov pre-commit
   ```

7. **Set up pre-commit hooks (REQUIRED - NOT OPTIONAL)**:
   ```bash
   pre-commit install
   ```
   
   ⚠️ **This step is MANDATORY!** Pre-commit hooks will automatically format your code with Black and organize imports with Ruff on every commit. This prevents CI/CD failures and ensures all code meets our formatting standards.
   
   After installing, the hooks will run automatically on every `git commit`. If formatting issues are found, they'll be fixed automatically, and you'll need to stage the changes and commit again.

8. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (for testing)
   ```

9. **Run tests** to verify setup:
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

4. **Format and lint your code** (REQUIRED - Pre-commit hooks do this automatically):
   
   If you have pre-commit hooks installed (step 7 in setup), **formatting happens automatically** when you commit. The hooks will:
   - Format code with Black
   - Organize imports with Ruff
   - Fix trailing whitespace and other issues
   
   If hooks find issues, they'll fix them automatically. You just need to:
   ```bash
   git add .
   git commit -m "your message"
   # If hooks made changes, add them and commit again:
   git add .
   git commit -m "your message"
   ```
   
   **Manual formatting** (if you didn't install pre-commit hooks or need to check):
   ```bash
   # Format code with Black
   black src/ tests/ examples/
   
   # Fix import organization and linting issues
   ruff check --fix src/ tests/ examples/
   
   # Verify everything passes
   black --check src/ tests/ examples/
   ruff check src/ tests/ examples/
   ```

5. **Type check** (optional but recommended):
   ```bash
   mypy src/
   ```

6. **Commit changes**:
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

Always use type hints with **Python 3.9+ native types** (`dict`, `list`, `tuple` instead of `Dict`, `List`, `Tuple` from typing):

```python
def analyze_data(
    symbol: str,
    period: int = 30,
    detailed: bool = False
) -> dict[str, Any]:
    """Analyze data for the given symbol."""
    pass
```

#### Docstrings

Use **Google-style docstrings**:

```python
def calculate_metrics(
    prices: pd.DataFrame,
    window: int = 20
) -> dict[str, float]:
    """
    Calculate technical metrics from price data.
    
    Args:
        prices: DataFrame with OHLCV data
        window: Rolling window size for calculations
        
    Returns:
        Dictionary with calculated metrics
        
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

### Code Quality Tools

Project Shri Sudarshan uses several tools to maintain code quality:

#### Black (Code Formatter)
- **Purpose**: Automatic code formatting
- **Configuration**: In `pyproject.toml` (line-length = 100)
- **Usage**: `black src/ tests/ examples/`
- **CI**: Must pass for all PRs

#### Ruff (Linter)
- **Purpose**: Fast Python linter (replaces flake8, isort, and more)
- **Configuration**: In `pyproject.toml` with rules:
  - `E/W` - pycodestyle errors and warnings
  - `F` - Pyflakes
  - `I` - Import sorting (isort)
  - `N` - PEP 8 naming conventions
  - `UP` - pyupgrade (modern Python syntax)
  - `B` - flake8-bugbear
  - `C4` - flake8-comprehensions
- **Usage**: 
  - Check: `ruff check src/ tests/ examples/`
  - Auto-fix: `ruff check --fix src/ tests/ examples/`
- **CI**: Must pass with zero errors
- **Key requirements**:
  - Imports must be sorted (stdlib, third-party, local)
  - Use native types: `dict`, `list`, `tuple` (not `Dict`, `List`, `Tuple` from typing)
  - Follow PEP 8 standards

#### mypy (Type Checker)
- **Purpose**: Static type checking
- **Configuration**: In `pyproject.toml`
- **Usage**: `mypy src/ --ignore-missing-imports`
- **CI**: Runs but doesn't block (continue-on-error: true)

#### Pre-commit Hooks
- **Purpose**: Automatically run checks before each commit
- **Setup**: `pre-commit install` (after installing pre-commit)
- **Configuration**: `.pre-commit-config.yaml`
- **Runs**: Black, Ruff, and other checks automatically
- **Benefits**: Catch issues early before pushing to CI

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

⚠️ **CRITICAL: Formatting Must Pass!** Your PR will be blocked if formatting checks fail.

1. **Verify formatting** (pre-commit hooks should have done this automatically):
   ```bash
   # Check formatting
   black --check src/ tests/ examples/
   ruff check src/ tests/ examples/
   ```
   
   If checks fail, fix them:
   ```bash
   # Fix formatting issues
   black src/ tests/ examples/
   ruff check --fix src/ tests/ examples/
   ```

2. **Update documentation** if needed

3. **Add tests** for new functionality

4. **Run full test suite**:
   ```bash
   pytest tests/
   ```

5. **Optional: Type check**:
   ```bash
   mypy src/
   ```

6. **Update CHANGELOG** (if applicable)

7. **Rebase on latest main**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

### What CI/CD Will Check

When you open a PR, automated checks will run:

1. **✅ Formatting Check (BLOCKING)**: 
   - Black formatting must pass
   - Ruff linting must pass with zero errors
   - **If these fail, PR cannot be merged**

2. **✅ Tests (BLOCKING)**:
   - All tests must pass
   - Minimum 40% code coverage required

3. **✅ Build (BLOCKING)**:
   - Package must build successfully

4. **ℹ️ Type Checking (NON-BLOCKING)**:
   - mypy warnings are shown but don't block merges

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

1. **Automated checks** will run (some are BLOCKING):
   - ✅ **Formatting** (Black & Ruff) - BLOCKING, must pass
   - ✅ **Tests** - BLOCKING, must pass
   - ✅ **Build** - BLOCKING, must pass
   - ℹ️ **Type checking** (mypy) - Non-blocking, warnings only
   - ℹ️ **Coverage** - Reported but doesn't block

2. **If formatting fails**:
   - Pull the latest changes
   - Run `black src/ tests/ examples/`
   - Run `ruff check --fix src/ tests/ examples/`
   - Commit and push the fixes
   - CI will re-run automatically

3. **Maintainer review**:
   - Code quality
   - Test coverage
   - Documentation
   - Adherence to standards

4. **Address feedback**:
   - Make requested changes
   - Push updates to same branch
   - PR updates automatically
   - **Remember to format any new changes!**

5. **Approval and merge**:
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

## Quick Reference: Formatting Commands

### Setup (One Time)
```bash
pip install black ruff mypy pre-commit
pre-commit install
```

### Before Every Commit
Pre-commit hooks run automatically! But if you need to run manually:

```bash
# Format code
black src/ tests/ examples/

# Fix linting and imports
ruff check --fix src/ tests/ examples/

# Verify everything passes
black --check src/ tests/ examples/
ruff check src/ tests/ examples/
```

### If CI Formatting Check Fails
```bash
# Pull latest changes
git pull origin your-branch-name

# Format everything
black src/ tests/ examples/
ruff check --fix src/ tests/ examples/

# Verify it's fixed
black --check src/ tests/ examples/
ruff check src/ tests/ examples/

# Commit and push
git add .
git commit -m "fix: apply Black and Ruff formatting"
git push
```

### Running Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_agents_base.py
```

---

## Questions?

- **Documentation**: See [Getting Started](getting_started.md), [Architecture](architecture.md)
- **Issues**: https://github.com/s-p-c-git/ShriSudarshan/issues
- **Discussions**: https://github.com/s-p-c-git/ShriSudarshan/discussions

---

Thank you for contributing to Project Shri Sudarshan! 🚀
