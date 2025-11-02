# Quick Reference Guide

## Commands

### Run Analysis
```bash
cd src
python main.py --symbol AAPL
```

### With Date Range
```bash
python main.py --symbol AAPL --start_date 2023-01-01 --end_date 2023-12-31
```

### Help
```bash
python main.py --help
```

## Project Structure

```
ShriSudarshan/
├── src/                          # Source code
│   ├── agents/                   # Agent implementations
│   │   ├── market_intelligence/  # 4 analyst agents
│   │   ├── strategy_research/    # 3 research agents
│   │   ├── execution/            # 2 trader agents
│   │   └── oversight/            # 3 management agents
│   ├── config/                   # Configuration
│   ├── memory/                   # 3-layer memory system
│   ├── orchestration/            # LangGraph workflow
│   └── main.py                   # Entry point
├── docs/                         # Documentation
├── tests/                        # Test suite
└── examples/                     # Example scripts
```

## Agent Teams

### Market Intelligence (Analysts)
1. **Fundamentals Analyst** - Financial reports & metrics
2. **Macro & News Analyst** - Economic data & news
3. **Sentiment Analyst** - Social media & market mood
4. **Technical Analyst** - Charts & indicators

### Strategy & Research (Debaters)
5. **Bullish Researcher** - Long position arguments
6. **Bearish Researcher** - Short position arguments
7. **Derivatives Strategist** - Options & futures strategies

### Execution (Traders)
8. **Equity Trader** - Stock order execution
9. **FnO Trader** - Options & futures execution

### Oversight & Learning (Management)
10. **Portfolio Manager** - Final approval authority
11. **Risk Manager** - Risk assessment & veto
12. **Reflective Agent** - Post-trade learning

## Workflow Phases

1. **Analysis** → Concurrent analyst execution
2. **Debate** → Multi-round bull/bear debate
3. **Strategy** → FnO strategy formulation
4. **Execution Planning** → Order specifications
5. **Risk Assessment** → Risk validation (gate)
6. **Portfolio Decision** → Final approval (gate)
7. **Execution** → Order submission
8. **Learning** → Post-trade reflection

## Memory System

### Working Memory
- **Type**: In-memory
- **Purpose**: Current session state
- **TTL**: Session duration

### Procedural Memory
- **Type**: Vector DB (ChromaDB)
- **Purpose**: Successful patterns
- **Access**: Similarity search

### Episodic Memory
- **Type**: SQL DB (SQLite/PostgreSQL)
- **Purpose**: Trade history
- **Access**: Structured queries

## Configuration (.env)

### Required
```bash
OPENAI_API_KEY=sk-...
```

### Optional
```bash
ALPHA_VANTAGE_API_KEY=...
PREMIUM_MODEL=gpt-4o
STANDARD_MODEL=gpt-4o-mini
```

### Risk Parameters
```bash
MAX_POSITION_SIZE=0.05        # 5%
MAX_PORTFOLIO_RISK=0.02       # 2%
MAX_SECTOR_CONCENTRATION=0.25 # 25%
```

## Key Files

### Documentation
- `APPROACH.md` - Implementation approach
- `IMPLEMENTATION_SUMMARY.md` - What's built
- `docs/architecture.md` - Architecture details
- `docs/getting_started.md` - Installation guide

### Code
- `src/main.py` - Entry point
- `src/config/settings.py` - Configuration
- `src/config/prompts.py` - Agent prompts
- `src/agents/base.py` - Base agent class
- `src/orchestration/workflow.py` - LangGraph workflow

## Common Tasks

### Add New Agent
1. Create class inheriting `BaseAgent`
2. Implement `analyze()` method
3. Add to workflow in `orchestration/workflow.py`

### Adjust Risk Parameters
Edit `.env`:
```bash
MAX_POSITION_SIZE=0.03  # Reduce to 3%
```

### Change LLM Model
Edit `.env`:
```bash
PREMIUM_MODEL=gpt-4o
STANDARD_MODEL=gpt-4o-mini
```

### Add Data Provider
1. Create provider class in `src/data/providers.py`
2. Integrate in relevant analyst agent

## Development

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
pytest
```

### Format Code
```bash
black src/
```

### Type Check
```bash
mypy src/
```

## Troubleshooting

### "OpenAI API key not configured"
- Copy `.env.example` to `.env`
- Add your API key

### "Module not found"
- Install dependencies: `pip install -r requirements.txt`
- Run from `src/` directory

### ChromaDB Warnings
- Optional for Phase 1
- Install: `pip install chromadb`

## Resources

- **GitHub**: https://github.com/s-p-c-git/ShriSudarshan
- **Issues**: https://github.com/s-p-c-git/ShriSudarshan/issues
- **Documentation**: See `docs/` directory

## Safety

### Paper Trading (Default)
- No real money at risk
- Orders simulated
- Safe for testing

### Live Trading
- Requires `--live-trading` flag
- Confirmation prompt
- Use with extreme caution

## Next Steps

1. **Install**: Clone repo, install deps, configure `.env`
2. **Run**: Test with `python main.py --symbol AAPL`
3. **Learn**: Read architecture docs
4. **Customize**: Adjust prompts and parameters
5. **Extend**: Add custom agents or strategies
