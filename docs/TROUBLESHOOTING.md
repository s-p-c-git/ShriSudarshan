# Troubleshooting Guide - Project Shri Sudarshan

## Overview

This guide helps diagnose and resolve common issues with Project Shri Sudarshan.

## Table of Contents

- [Installation Issues](#installation-issues)
- [API Key and Configuration Issues](#api-key-and-configuration-issues)
- [Data Provider Issues](#data-provider-issues)
- [Agent Execution Issues](#agent-execution-issues)
- [Memory System Issues](#memory-system-issues)
- [Workflow Orchestration Issues](#workflow-orchestration-issues)
- [Performance Issues](#performance-issues)
- [Common Error Messages](#common-error-messages)

---

## Installation Issues

### Problem: `ModuleNotFoundError` when importing modules

**Symptoms**:
```
ModuleNotFoundError: No module named 'langgraph'
ModuleNotFoundError: No module named 'pydantic'
```

**Solution**:
1. Ensure virtual environment is activated:
   ```bash
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. If installation fails, try upgrading pip:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Problem: ChromaDB installation fails

**Symptoms**:
```
ERROR: Failed building wheel for chromadb
```

**Solution**:
ChromaDB may have system dependencies. Try:

1. **Linux**:
   ```bash
   sudo apt-get install build-essential python3-dev
   pip install chromadb
   ```

2. **macOS**:
   ```bash
   brew install cmake
   pip install chromadb
   ```

3. **Alternative**: The system gracefully degrades if ChromaDB is unavailable. Procedural memory will use in-memory fallback.

### Problem: `ImportError` for TA-Lib

**Symptoms**:
```
ImportError: cannot import name 'talib'
```

**Solution**:
TA-Lib is optional and not required for basic operation:

1. **To install** (requires system library first):
   - Linux: `sudo apt-get install ta-lib`
   - macOS: `brew install ta-lib`
   - Then: `pip install TA-Lib`

2. **To skip**: Comment out TA-Lib in `requirements.txt` if not needed.

---

## API Key and Configuration Issues

### Problem: `OPENAI_API_KEY` not found

**Symptoms**:
```
Error: OPENAI_API_KEY environment variable not set
```

**Solution**:
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

3. Verify the key is loaded:
   ```python
   from src.config import settings
   print(settings.openai_api_key)  # Should not be empty
   ```

### Problem: Invalid API key

**Symptoms**:
```
openai.error.AuthenticationError: Incorrect API key provided
```

**Solution**:
1. Verify your API key at https://platform.openai.com/api-keys
2. Ensure no extra spaces or quotes in `.env` file
3. Check that key starts with `sk-`
4. Regenerate key if necessary

### Problem: Rate limit errors

**Symptoms**:
```
openai.error.RateLimitError: Rate limit exceeded
```

**Solution**:
1. **Reduce concurrent analysis**:
   ```
   ENABLE_CONCURRENT_ANALYSIS=false
   ```

2. **Use cheaper model for analysis**:
   ```
   STANDARD_MODEL=gpt-3.5-turbo
   ```

3. **Add delays between API calls** (modify code if needed)

4. **Upgrade OpenAI tier** at https://platform.openai.com/account/limits

---

## Data Provider Issues

### Problem: `yfinance` returns empty data

**Symptoms**:
- Price history DataFrame is empty
- Fundamentals dict has no data
- `None` returned for current price

**Solution**:
1. **Check symbol validity**:
   ```python
   import yfinance as yf
   ticker = yf.Ticker("AAPL")
   print(ticker.info)  # Should return data
   ```

2. **Try different period/interval**:
   ```python
   # Instead of:
   history = provider.get_price_history("AAPL", period="1d")
   
   # Try:
   history = provider.get_price_history("AAPL", period="5d")
   ```

3. **Check network connectivity**:
   ```bash
   ping finance.yahoo.com
   ```

4. **Use date ranges instead of periods**:
   ```python
   from datetime import datetime, timedelta
   end = datetime.now()
   start = end - timedelta(days=30)
   history = provider.get_price_history(
       "AAPL",
       start=start.strftime("%Y-%m-%d"),
       end=end.strftime("%Y-%m-%d"),
   )
   ```

### Problem: Options chain data unavailable

**Symptoms**:
```python
options = provider.get_options_chain("AAPL")
# options['calls'] is empty
```

**Solution**:
1. Not all stocks have options. Verify at https://finance.yahoo.com/quote/AAPL/options

2. Check available expiries first:
   ```python
   expiries = provider.get_available_expiries("AAPL")
   print(expiries)  # Should show list of dates
   ```

3. Use specific expiry:
   ```python
   options = provider.get_options_chain("AAPL", expiry_date=expiries[0])
   ```

### Problem: News articles not found

**Symptoms**:
- `get_company_news()` returns empty list
- No sentiment data available

**Solution**:
1. **Increase lookback period**:
   ```python
   news = provider.get_company_news("AAPL", days_back=30)
   ```

2. **Try market news instead**:
   ```python
   news = provider.get_market_news(days_back=7)
   ```

3. **Check if symbol is actively traded**:
   - Major stocks (AAPL, GOOGL, MSFT) should always have news
   - Smaller stocks may have infrequent news

---

## Agent Execution Issues

### Problem: Agent analysis fails with error

**Symptoms**:
```
[Fundamentals Analyst] Analysis failed: <error message>
```

**Solution**:
1. **Check error message in logs**:
   - Look for specific exception details
   - Common issues: missing data, invalid response format

2. **Verify data provider works**:
   ```python
   from src.data.providers import MarketDataProvider
   provider = MarketDataProvider()
   fundamentals = provider.get_fundamentals("AAPL")
   print(fundamentals)  # Should have data
   ```

3. **Test agent in isolation**:
   ```python
   from src.agents.market_intelligence import FundamentalsAnalyst
   
   agent = FundamentalsAnalyst()
   context = {"symbol": "AAPL"}
   report = await agent.analyze(context)
   print(report)
   ```

4. **Reduce LLM temperature** for more deterministic output:
   - Edit agent initialization to use lower temperature (0.3-0.5)

### Problem: LLM response parsing fails

**Symptoms**:
```
WARNING: Failed to parse LLM response as JSON, using defaults
```

**Solution**:
This is a warning, not an error. The system continues with defaults:

1. **To reduce occurrences**:
   - Use lower temperature (0.3-0.5)
   - Improve system prompts in `src/config/prompts.py`

2. **To debug**:
   - Add logging to see raw LLM response:
     ```python
     response = await self._generate_response(input_text)
     logger.debug("Raw LLM response", response=response)
     ```

3. **Most common cause**: LLM includes explanation before/after JSON. The code handles this by extracting JSON from markdown code blocks.

### Problem: Agent returns low confidence scores

**Symptoms**:
- All agents report confidence_level < 5
- Analysis seems incomplete

**Solution**:
1. **Ensure sufficient data available**:
   - Check that market data provider returns complete data
   - Verify news provider has recent articles

2. **Use premium model for all agents** (expensive):
   ```
   STANDARD_MODEL=gpt-4o
   ```

3. **Review system prompts** in `src/config/prompts.py`:
   - Ensure prompts clearly define confidence criteria
   - Add examples of high-confidence scenarios

---

## Memory System Issues

### Problem: Episodic memory database errors

**Symptoms**:
```
sqlalchemy.exc.OperationalError: unable to open database file
```

**Solution**:
1. **Check database path**:
   ```bash
   # Default location
   ls -la episodic_memory.db
   ```

2. **Ensure write permissions**:
   ```bash
   chmod 644 episodic_memory.db
   ```

3. **Specify database path in `.env`**:
   ```
   EPISODIC_MEMORY_DB=sqlite:///./data/trades.db
   ```

4. **Initialize database** if missing:
   ```python
   from src.memory import EpisodicMemory
   memory = EpisodicMemory()
   # Database is auto-created
   ```

### Problem: Procedural memory ChromaDB connection fails

**Symptoms**:
```
chromadb.errors.ConnectionError
```

**Solution**:
System gracefully falls back to in-memory storage:

1. **Verify ChromaDB installation**:
   ```python
   import chromadb
   print(chromadb.__version__)
   ```

2. **Check disk space** (ChromaDB persists to disk):
   ```bash
   df -h
   ```

3. **Use in-memory mode** (data lost on restart):
   ```python
   # In src/memory/procedural.py, use:
   client = chromadb.Client()  # In-memory
   # Instead of:
   client = chromadb.PersistentClient(path="./chroma_db")
   ```

### Problem: Working memory not clearing

**Symptoms**:
- Old data persists across runs
- Memory usage grows over time

**Solution**:
1. **Working memory auto-expires** based on TTL (default 3600s)

2. **Manual cleanup**:
   ```python
   from src.memory import WorkingMemory
   memory = WorkingMemory()
   memory.clear_expired()  # Remove expired entries
   memory.clear_all()      # Remove everything
   ```

3. **Adjust TTL in `.env`**:
   ```
   WORKING_MEMORY_TTL=1800  # 30 minutes
   ```

---

## Workflow Orchestration Issues

### Problem: Workflow stops at approval gate

**Symptoms**:
- Workflow reaches risk assessment or portfolio decision
- Execution never happens
- No error messages

**Cause**: Risk Manager or Portfolio Manager rejected the trade.

**Solution**:
1. **Check logs** for rejection reason:
   ```
   [Risk Manager] Trade rejected: Position size exceeds limit
   ```

2. **Adjust risk parameters in `.env`**:
   ```
   MAX_POSITION_SIZE=0.10        # Increase from 5% to 10%
   MAX_PORTFOLIO_RISK=0.03       # Increase from 2% to 3%
   MAX_SECTOR_CONCENTRATION=0.40 # Increase from 25% to 40%
   ```

3. **Review workflow state**:
   ```python
   # In workflow, print state after each phase
   print(f"Risk approved: {state['risk_approved']}")
   print(f"Final approved: {state['final_approved']}")
   ```

### Problem: Debate phase runs too long

**Symptoms**:
- System seems hung during debate phase
- Takes minutes to complete

**Solution**:
1. **Reduce debate rounds**:
   ```
   MAX_DEBATE_ROUNDS=2  # Default is 3
   ```

2. **Disable concurrent execution**:
   ```
   ENABLE_CONCURRENT_ANALYSIS=false
   ```

3. **Use faster models**:
   ```
   STANDARD_MODEL=gpt-3.5-turbo
   ```

### Problem: Workflow errors not handled

**Symptoms**:
- Unhandled exception crashes the system
- No graceful degradation

**Solution**:
1. **Check workflow phase implementation**:
   - Each phase should have try-except blocks
   - Errors should be logged to state['errors']

2. **Review logs** for exception details:
   ```bash
   # Check application logs
   tail -f app.log
   ```

3. **Add error handling** in workflow phases:
   ```python
   try:
       result = await agent.analyze(context)
   except Exception as e:
       logger.error("Agent failed", error=str(e))
       state["errors"].append(f"Agent error: {str(e)}")
       result = None  # Use default/fallback
   ```

---

## Performance Issues

### Problem: Analysis phase takes too long

**Symptoms**:
- Analysts take > 60 seconds to complete
- System feels slow

**Solution**:
1. **Enable concurrent execution** (if not already):
   ```
   ENABLE_CONCURRENT_ANALYSIS=true
   ```

2. **Use faster models for non-critical agents**:
   ```
   STANDARD_MODEL=gpt-3.5-turbo
   ```

3. **Reduce data processing**:
   - Limit price history to necessary period
   - Reduce news articles fetched
   - Cache data providers

4. **Profile slow agents**:
   ```python
   import time
   start = time.time()
   report = await agent.analyze(context)
   duration = time.time() - start
   print(f"Agent took {duration:.2f}s")
   ```

### Problem: High API costs

**Symptoms**:
- OpenAI bill is high
- Each analysis costs significant money

**Solution**:
1. **Use cheaper models**:
   ```
   STANDARD_MODEL=gpt-3.5-turbo
   PREMIUM_MODEL=gpt-4o-mini
   ```

2. **Reduce debate rounds**:
   ```
   MAX_DEBATE_ROUNDS=1
   ```

3. **Disable concurrent analysis** (reduces parallel API calls):
   ```
   ENABLE_CONCURRENT_ANALYSIS=false
   ```

4. **Cache agent responses** (implement caching layer)

5. **Reduce analysis frequency** (don't analyze every minute)

### Problem: Memory usage grows over time

**Symptoms**:
- System uses more RAM over time
- Eventually crashes with OOM error

**Solution**:
1. **Clear working memory regularly**:
   ```python
   memory.clear_expired()
   ```

2. **Limit procedural memory size**:
   - Implement max collection size in ChromaDB
   - Periodically prune old patterns

3. **Close database connections**:
   ```python
   episodic_memory.close()
   ```

4. **Monitor memory usage**:
   ```python
   import psutil
   process = psutil.Process()
   print(f"Memory: {process.memory_info().rss / 1024 ** 2:.2f} MB")
   ```

---

## Common Error Messages

### `ValidationError: validation error for FundamentalsReport`

**Cause**: Data doesn't match Pydantic schema

**Solution**:
1. Check field types match schema
2. Ensure required fields are provided
3. Verify value ranges (e.g., confidence 0.0-1.0)

### `RuntimeError: Event loop is closed`

**Cause**: Async/await issues

**Solution**:
1. Use `asyncio.run()` for top-level calls:
   ```python
   import asyncio
   asyncio.run(main())
   ```

2. Don't close event loop manually

### `FileNotFoundError: [Errno 2] No such file or directory: '.env'`

**Cause**: Missing `.env` file

**Solution**:
```bash
cp .env.example .env
# Edit .env with your settings
```

### `AttributeError: 'NoneType' object has no attribute 'value'`

**Cause**: Agent returned None instead of report

**Solution**:
1. Check agent logs for errors
2. Verify data provider returns data
3. Add null checks:
   ```python
   if report is None:
       logger.error("Agent returned None")
       return
   ```

---

## Getting Help

If you can't resolve an issue:

1. **Check logs** for detailed error messages
2. **Search GitHub issues**: https://github.com/s-p-c-git/ShriSudarshan/issues
3. **Create new issue** with:
   - Error message
   - Steps to reproduce
   - Environment details (OS, Python version)
   - Relevant code snippets
4. **Review documentation**:
   - [Architecture](architecture.md)
   - [Getting Started](getting_started.md)
   - [API Reference](API_REFERENCE.md)

---

## Debug Mode

Enable debug logging for more information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or in `.env`:
```
LOG_LEVEL=DEBUG
```

---

## Known Issues

### Issue: Technical indicators return None with insufficient data

**Status**: Expected behavior

**Workaround**: Use longer history periods (e.g., 1y instead of 1mo)

### Issue: Options data unavailable for some symbols

**Status**: Data provider limitation (yfinance)

**Workaround**: Use symbols with active options markets

### Issue: Sentiment analysis may be inaccurate

**Status**: Uses simple keyword matching

**Future**: Plan to integrate advanced NLP models

---

## Prevention Best Practices

1. **Always use virtual environment**
2. **Keep dependencies updated**: `pip install --upgrade -r requirements.txt`
3. **Monitor API usage** to avoid rate limits
4. **Test with small datasets** before full runs
5. **Enable logging** for debugging
6. **Use paper trading mode** by default
7. **Backup episodic memory database** regularly
8. **Review agent outputs** before trusting decisions

---

*Last updated: 2025-11-02*
