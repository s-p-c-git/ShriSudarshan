# Migration Guide: Adding FinBERT and FinGPT to Your Setup

This guide helps you upgrade your existing Project Shri Sudarshan installation to use the new FinBERT and FinGPT agents.

## Prerequisites

Before starting, ensure you have:
- Python 3.9 or higher
- Working installation of Project Shri Sudarshan
- At least 8GB of RAM (16GB recommended for FinGPT)
- 10GB of free disk space for models

## Step 1: Update Dependencies

Update your installation with the new dependencies:

```bash
cd ShriSudarshan
pip install -r requirements.txt --upgrade
```

This will install:
- `transformers>=4.35.0` - Hugging Face Transformers library
- `torch>=2.0.0` - PyTorch for model inference
- `accelerate>=0.25.0` - Hardware acceleration support
- `bitsandbytes>=0.41.0` - 8-bit quantization for FinGPT

**Note:** If you encounter issues with PyTorch, install it separately first:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

For GPU support (recommended for FinGPT):
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Step 2: Update Configuration

Update your `.env` file with the new configuration options:

```bash
# Add these lines to your .env file

# FinBERT Configuration
FINBERT_MODEL=ProsusAI/finbert

# FinGPT Configuration  
FINGPT_MODEL=FinGPT/fingpt-forecaster_dow30_llama2-7b_lora
FINGPT_USE_LOCAL=true
```

## Step 3: Verify Installation

Test that the new agents can be imported:

```bash
python -c "
from src.agents.market_intelligence import FinBERTSentimentAnalyst, FinGPTGenerativeAnalyst
print('✓ FinBERT and FinGPT agents imported successfully')
"
```

## Step 4: Test with Example

Run the provided example to verify everything works:

```bash
cd examples
python finbert_fingpt_usage.py
```

**Expected output:**
- FinBERT sentiment analysis results
- FinGPT generative analysis results
- Combined workflow demonstration

## Step 5: Run Your First Analysis

Modify your existing analysis code to include the new agents. Here's a minimal example:

```python
import asyncio
from src.orchestration import TradingWorkflow
from src.orchestration.state import create_initial_state

async def run_analysis():
    # Create workflow
    workflow = TradingWorkflow()
    
    # Create initial state with symbol
    state = create_initial_state(symbol="AAPL")
    
    # Run workflow (now includes FinBERT and FinGPT)
    result = await workflow.graph.ainvoke(state)
    
    # Access new agent reports
    finbert_report = result["analyst_reports"].get("finbert")
    fingpt_report = result["analyst_reports"].get("fingpt")
    
    if finbert_report:
        print(f"FinBERT Sentiment: {finbert_report.sentiment.value}")
        print(f"Sentiment Score: {finbert_report.sentiment_score:.2f}")
    
    if fingpt_report:
        print(f"FinGPT Insights: {fingpt_report.key_insights}")

asyncio.run(run_analysis())
```

## Troubleshooting

### Issue: Import Error - No module named 'transformers'

**Solution:** Install transformers:
```bash
pip install transformers torch
```

### Issue: Model Download is Slow

**Solution:** Models are downloaded on first use. FinBERT (~500MB) and FinGPT (~4GB) will be cached in `~/.cache/huggingface/`.

To pre-download models:
```python
from transformers import AutoTokenizer, AutoModel
AutoTokenizer.from_pretrained("ProsusAI/finbert")
AutoModel.from_pretrained("ProsusAI/finbert")
```

### Issue: Out of Memory with FinGPT

**Solution:** FinGPT is resource-intensive. Options:

1. Use FinBERT only (set `FINGPT_USE_LOCAL=false` in `.env`)
2. Use smaller FinGPT variant
3. Upgrade to a machine with more RAM/GPU
4. Use quantization (already enabled via bitsandbytes)

### Issue: FinGPT is Too Slow

**Solution:** 
- Use GPU instead of CPU (10-20x faster)
- Reduce `max_length` in generation
- Use FinGPT selectively (only when FinBERT flags strong sentiment)

## Performance Optimization

### FinBERT Performance Tips

1. **Batch Processing:** Analyze multiple texts together
   ```python
   context = {"symbol": "AAPL", "texts": list_of_headlines}
   ```

2. **Caching:** Cache FinBERT results for frequently analyzed texts

3. **Concurrent Analysis:** Already enabled by default in workflow

### FinGPT Performance Tips

1. **Selective Usage:** Only use FinGPT when needed
   ```python
   # Example: Only trigger FinGPT for strong sentiment
   if abs(finbert_report.sentiment_score) > 0.5:
       fingpt_report = await fingpt_analyst.analyze(context)
   ```

2. **Shorter Prompts:** Limit input text to 1000-2000 tokens

3. **Lower max_length:** Reduce generated text length for faster inference

## Backward Compatibility

The new agents are **fully backward compatible**:

- Existing workflows continue to work unchanged
- Traditional sentiment analyst remains available
- New agents run alongside existing agents
- Can disable new agents by removing from workflow

To disable new agents temporarily, modify `src/orchestration/workflow.py` and comment out the FinBERT/FinGPT sections.

## Next Steps

1. Review the [FinBERT and FinGPT Integration Guide](FINBERT_FINGPT_INTEGRATION.md)
2. Experiment with different analysis types in FinGPT
3. Compare results between traditional and FinBERT sentiment analysis
4. Fine-tune model selection based on your use case

## Support

If you encounter issues:
1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review [Testing Documentation](TESTING.md)
3. Open an issue on GitHub with:
   - Python version
   - Operating system
   - Full error message
   - Steps to reproduce

## Rollback

If you need to rollback:

```bash
git checkout main
pip install -r requirements.txt --force-reinstall
```

Then restore your `.env` file from backup.
