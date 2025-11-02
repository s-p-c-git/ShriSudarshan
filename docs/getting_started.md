# Getting Started with Project Shri Sudarshan

## Installation

### Prerequisites

1. **Python 3.9 or higher**
   ```bash
   python --version
   ```

2. **pip package manager**
   ```bash
   pip --version
   ```

### Step 1: Clone the Repository

```bash
git clone https://github.com/s-p-c-git/ShriSudarshan.git
cd ShriSudarshan
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```bash
   # Required
   OPENAI_API_KEY=sk-your-openai-api-key-here
   
   # Optional (for enhanced features)
   ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
   ```

## Basic Usage

### Running Analysis

Analyze a single stock symbol:

```bash
cd src
python main.py --symbol AAPL
```

### With Date Range

Analyze with specific date range:

```bash
python main.py --symbol AAPL --start_date 2023-01-01 --end_date 2023-01-31
```

### Command Line Options

```
--symbol SYMBOL        Stock symbol to analyze (required)
--start_date DATE      Start date (YYYY-MM-DD)
--end_date DATE        End date (YYYY-MM-DD)
--paper-trading        Enable paper trading (default)
--live-trading         Enable live trading (CAUTION!)
--log-level LEVEL      Set logging level (DEBUG, INFO, WARNING, ERROR)
```

## Understanding the Output

The system will process through these phases:

1. **Analysis Phase**: Market intelligence agents analyze the symbol
2. **Debate Phase**: Bullish and bearish researchers debate
3. **Strategy Phase**: Derivatives strategist formulates strategy
4. **Execution Planning**: Traders create execution plan
5. **Risk Assessment**: Risk manager validates risk parameters
6. **Portfolio Decision**: Portfolio manager approves/rejects
7. **Execution**: (Paper trading mode by default)
8. **Learning**: Reflective agent logs insights

### Sample Output

```
============================================================
Starting trading workflow for AAPL
============================================================

[Analysis Phase] Analyzing AAPL
[Debate Phase] Debating strategy for AAPL
[Strategy Phase] Formulating strategy for AAPL
[Execution Planning Phase] Planning execution for AAPL
[Risk Assessment Phase] Assessing risk for AAPL
[Portfolio Decision Phase] Making decision for AAPL
[Execution Phase] Executing strategy for AAPL
[Learning Phase] Logging trade for AAPL

============================================================
Workflow completed for AAPL
Final phase: learning
============================================================

============================================================
WORKFLOW SUMMARY
============================================================
Symbol: AAPL
Final Phase: learning
Analysis Complete: True
Debate Complete: True
Strategy Complete: True
Risk Approved: True
Final Approval: True
Execution Complete: True
============================================================
```

## Current Implementation Status

### ✅ Implemented
- Project structure and configuration
- Base agent classes
- Memory system architecture
- LangGraph workflow orchestration
- State management
- CLI interface
- Configuration management

### 🚧 In Progress (Placeholder implementations)
- Individual agent implementations
- Data provider integrations
- Debate mechanism
- Execution logic
- Risk calculations
- Learning algorithms

## Next Steps

### For Development

1. **Implement Market Intelligence Agents**
   - Connect to data providers (yfinance, Alpha Vantage)
   - Parse and structure data
   - Generate comprehensive reports

2. **Build Debate Mechanism**
   - Multi-round structured debate
   - Argument extraction and evaluation
   - Convergence criteria

3. **Add Risk Management**
   - Portfolio-level calculations
   - VaR computation
   - Concentration checks

### For Users

1. **Familiarize with the Architecture**
   - Read `docs/architecture.md`
   - Review `APPROACH.md`
   - Understand agent roles

2. **Configure Your Environment**
   - Set up API keys properly
   - Adjust risk parameters in `.env`
   - Choose appropriate LLM models

3. **Start with Paper Trading**
   - Test with small positions
   - Review agent outputs
   - Understand decision flow

## Troubleshooting

### "OpenAI API key not configured"

Make sure you've:
1. Copied `.env.example` to `.env`
2. Added your OpenAI API key to `.env`
3. The key starts with `sk-`

### Import Errors

Make sure you're running from the correct directory:
```bash
cd src
python main.py --symbol AAPL
```

Or install the package in development mode:
```bash
pip install -e .
```

### ChromaDB Warnings

ChromaDB is optional for Phase 1. The system will operate in mock mode without it. To enable:
```bash
pip install chromadb
```

## Configuration Options

### Risk Parameters

Edit `.env` to adjust risk management:

```bash
MAX_POSITION_SIZE=0.05        # 5% max per position
MAX_PORTFOLIO_RISK=0.02       # 2% VaR threshold
MAX_SECTOR_CONCENTRATION=0.25 # 25% max per sector
```

### LLM Models

Choose between different models:

```bash
# For critical decisions (expensive but better)
PREMIUM_MODEL=gpt-4o

# For routine analysis (cheaper)
STANDARD_MODEL=gpt-4o-mini
```

### Agent Configuration

```bash
ENABLE_CONCURRENT_ANALYSIS=true  # Run analysts in parallel
MAX_DEBATE_ROUNDS=3              # Debate iteration limit
ANALYSIS_TIMEOUT_SECONDS=30      # Analysis timeout
```

## Resources

- **Architecture**: `docs/architecture.md`
- **Approach Document**: `APPROACH.md`
- **API Reference**: Coming soon
- **Agent Specifications**: Coming soon

## Getting Help

- Check documentation in `docs/`
- Review example code in `examples/`
- Read inline code comments
- Check issue tracker on GitHub

## Safety Notes

### Paper Trading (Default)
- No real money at risk
- Orders are simulated
- Safe for testing and learning

### Live Trading
- Requires explicit `--live-trading` flag
- Confirmation prompt required
- Real money at risk
- Use with caution and start small

## What's Next?

Now that you have the basic system running, explore:

1. **Agent Customization**: Modify prompts in `src/config/prompts.py`
2. **Risk Parameters**: Adjust limits in `.env`
3. **Data Sources**: Add new providers in `src/data/`
4. **Custom Strategies**: Extend agent logic

Happy trading! 📈
