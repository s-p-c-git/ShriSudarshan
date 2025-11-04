# FinBERT and FinGPT Integration Guide

## Overview

This document describes the integration of specialized financial models FinBERT and FinGPT into the Market Intelligence Team of Project Shri Sudarshan.

## New Agents

### 1. FinBERT Sentiment Analyst

**Purpose:** High-speed, specialized sentiment analysis using the FinBERT model pre-trained on financial text.

**Model:** ProsusAI/finbert (Hugging Face)

**Key Features:**
- Pre-trained on financial corpus for domain-specific sentiment
- Fast batch processing of news, headlines, and social media
- Outputs standardized sentiment scores (positive, negative, neutral)
- Quantitative sentiment score from -1 (very negative) to +1 (very positive)

**Usage:**

```python
from src.agents.market_intelligence import FinBERTSentimentAnalyst

analyst = FinBERTSentimentAnalyst()

context = {
    "symbol": "AAPL",
    "texts": [
        "Apple announces record quarterly earnings",
        "Market analysts upgrade AAPL to buy",
    ]
}

report = await analyst.analyze(context)
print(f"Sentiment: {report.sentiment.value}")
print(f"Score: {report.sentiment_score:.2f}")
print(f"Positive: {report.positive_score:.2f}")
print(f"Negative: {report.negative_score:.2f}")
```

**Output Schema (`FinBERTSentimentReport`):**
- `sentiment`: Overall sentiment (BULLISH, BEARISH, NEUTRAL)
- `sentiment_score`: Float from -1.0 to 1.0
- `positive_score`: Float from 0.0 to 1.0
- `negative_score`: Float from 0.0 to 1.0
- `neutral_score`: Float from 0.0 to 1.0
- `text_analyzed`: List of texts analyzed (up to 5 for reference)
- `confidence`: Confidence level (0.0 to 1.0)

### 2. FinGPT Generative Analyst

**Purpose:** In-depth generative analysis for summarization, question-answering, and qualitative insights.

**Model:** FinGPT/fingpt-forecaster_dow30_llama2-7b_lora (Hugging Face)

**Key Features:**
- Generative model fine-tuned for financial tasks
- Supports multiple analysis types (filings, transcripts, news)
- Produces structured insights, risks, and opportunities
- Human-readable summaries and recommendations

**Usage:**

```python
from src.agents.market_intelligence import FinGPTGenerativeAnalyst

analyst = FinGPTGenerativeAnalyst(use_local=True)

context = {
    "symbol": "AAPL",
    "text": "Apple's Q3 earnings report shows...",
    "analysis_type": "summarize_filing"  # or "analyze_transcript", "analyze_news", "general_analysis"
}

report = await analyst.analyze(context)
print(f"Insights: {report.key_insights}")
print(f"Risks: {report.risks_identified}")
print(f"Opportunities: {report.opportunities_identified}")
```

**Analysis Types:**
1. `summarize_filing` - Analyze financial filings (10-K, 10-Q)
2. `analyze_transcript` - Analyze earnings call transcripts
3. `analyze_news` - Analyze news articles
4. `general_analysis` - General-purpose financial analysis

**Output Schema (`FinGPTGenerativeReport`):**
- `analysis_type`: Type of analysis performed
- `key_insights`: List of key insights (up to 5)
- `risks_identified`: List of identified risks (up to 3)
- `opportunities_identified`: List of identified opportunities (up to 3)
- `detailed_summary`: Detailed text summary (up to 1000 chars)
- `confidence`: Confidence level (0.0 to 1.0)

## Workflow Integration

### Hybrid Dual-Agent Approach

The two agents work together in the analysis phase:

1. **FinBERT** runs first for rapid sentiment triage on news and headlines
2. **FinGPT** follows with deep qualitative analysis when needed
3. Portfolio Manager receives both quantitative sentiment and qualitative summary
4. Results are consolidated with other analyst reports for decision-making

### Analysis Phase Flow

```
Market Intelligence Phase
├── Fundamentals Analyst
├── Technical Analyst
├── Sentiment Analyst (traditional)
├── Macro/News Analyst
├── FinBERT Sentiment Analyst ← New
└── FinGPT Generative Analyst ← New
```

Both new agents run concurrently with traditional analysts, with results stored in `state["analyst_reports"]`:

```python
state["analyst_reports"] = {
    "fundamentals": fundamentals_report,
    "technical": technical_report,
    "sentiment": sentiment_report,
    "macro_news": macro_news_report,
    "finbert": finbert_report,      # New
    "fingpt": fingpt_report,         # New
}
```

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# FinBERT Configuration
FINBERT_MODEL=ProsusAI/finbert

# FinGPT Configuration
FINGPT_MODEL=FinGPT/fingpt-forecaster_dow30_llama2-7b_lora
FINGPT_USE_LOCAL=true  # Set to false for API-based generation
```

### Dependencies

Install required packages:

```bash
pip install transformers>=4.35.0 torch>=2.0.0 accelerate>=0.25.0 bitsandbytes>=0.41.0
```

Or update from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Performance Considerations

### FinBERT
- **Fast:** Typically processes 10-20 texts in < 1 second
- **Memory:** ~500MB GPU/CPU memory
- **Scalable:** Can batch process hundreds of headlines efficiently

### FinGPT
- **Slower:** Generative analysis takes 5-15 seconds depending on prompt
- **Memory:** ~4GB+ GPU memory (with 8-bit quantization) or ~14GB CPU
- **Resource Intensive:** Recommend using for targeted deep-dive analysis

**Recommendation:** Use FinBERT for high-volume sentiment screening, trigger FinGPT only for flagged assets or scheduled deep analysis.

## Model Loading

Both agents use lazy loading - models are only loaded when first needed:

```python
# Model not loaded yet
analyst = FinBERTSentimentAnalyst()

# Model loads on first analyze() call
report = await analyst.analyze(context)

# Subsequent calls reuse loaded model
report2 = await analyst.analyze(context2)
```

## Error Handling

Both agents implement graceful error handling:

```python
try:
    report = await analyst.analyze(context)
except ImportError as e:
    # transformers/torch not installed
    print("Install dependencies: pip install transformers torch")
except Exception as e:
    # Model loading or inference error
    # Agent returns a report with confidence=0.0 and error message
    print(f"Analysis failed: {e}")
```

## Testing

Run tests for the new agents:

```bash
pytest tests/test_agents_finbert_fingpt.py -v
```

Tests use mocks to avoid requiring actual model downloads during testing.

## Comparison with Traditional Sentiment Analyst

| Feature | Traditional Sentiment | FinBERT | FinGPT |
|---------|----------------------|---------|--------|
| **Speed** | Fast (LLM call) | Very Fast (local inference) | Slow (generative) |
| **Depth** | Moderate | Quantitative only | Deep qualitative |
| **Specialization** | General | Financial sentiment | Financial domain |
| **Output** | Sentiment + summary | Precise scores | Insights + reasoning |
| **Use Case** | General market mood | High-volume screening | Deep analysis |

**Recommendation:** Use all three in combination:
- Traditional Sentiment for overall market mood and context
- FinBERT for precise, quantitative sentiment scores
- FinGPT for qualitative insights and recommendations

## Future Enhancements

Potential improvements for future versions:

1. **Fine-tuning:** Custom fine-tune FinBERT on specific asset classes
2. **API Integration:** Support for FinGPT API endpoints when available
3. **Caching:** Cache FinGPT responses for frequently analyzed texts
4. **Ensemble:** Combine FinBERT + Traditional Sentiment with weighted voting
5. **Real-time:** Stream FinBERT analysis on live news feeds

## References

- FinBERT Paper: [FinBERT: Financial Sentiment Analysis with Pre-trained Language Models](https://arxiv.org/abs/1908.10063)
- FinBERT Model: [ProsusAI/finbert on Hugging Face](https://huggingface.co/ProsusAI/finbert)
- FinGPT: [FinGPT: Open-Source Financial Large Language Models](https://github.com/AI4Finance-Foundation/FinGPT)
- FinGPT Models: [FinGPT on Hugging Face](https://huggingface.co/FinGPT)

## Support

For issues or questions:
1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review [Testing Documentation](TESTING.md)
3. Open an issue on GitHub with details about your environment and error messages
