"""
Tests for FinBERT and FinGPT Market Intelligence agents.

Tests the specialized financial model agents:
- FinBERTSentimentAnalyst
- FinGPTGenerativeAnalyst
"""

import pytest

from src.data.schemas import (
    AgentRole,
    FinBERTSentimentReport,
    FinGPTGenerativeReport,
    Sentiment,
)


# =============================================================================
# FinBERT Sentiment Analyst Tests
# =============================================================================


@pytest.mark.asyncio
async def test_finbert_analyst_basic_analysis(sample_context):
    """Test FinBERT analyst produces valid report with mock."""
    from src.agents.market_intelligence import FinBERTSentimentAnalyst

    agent = FinBERTSentimentAnalyst()

    # Add texts to context
    context = {
        **sample_context,
        "texts": [
            "Apple announces record quarterly earnings with strong iPhone sales",
            "Market analysts upgrade AAPL stock to buy rating",
        ],
    }

    # Mock the model loading and analysis to avoid dependencies
    def mock_aggregate(texts):
        return {
            "sentiment": "positive",
            "positive": 0.85,
            "negative": 0.10,
            "neutral": 0.05,
            "confidence": 0.75,
        }

    agent._aggregate_sentiments = mock_aggregate

    report = await agent.analyze(context)

    assert isinstance(report, FinBERTSentimentReport)
    assert report.agent_role == AgentRole.FINBERT_SENTIMENT_ANALYST
    assert report.symbol == sample_context["symbol"]
    assert report.confidence >= 0.0
    assert report.summary is not None


@pytest.mark.asyncio
async def test_finbert_analyst_sentiment_scores(sample_context):
    """Test FinBERT analyst includes sentiment scores."""
    from src.agents.market_intelligence import FinBERTSentimentAnalyst

    agent = FinBERTSentimentAnalyst()

    context = {
        **sample_context,
        "texts": ["Positive financial news"],
    }

    # Mock the analysis
    def mock_aggregate(texts):
        return {
            "sentiment": "positive",
            "positive": 0.75,
            "negative": 0.15,
            "neutral": 0.10,
            "confidence": 0.60,
        }

    agent._aggregate_sentiments = mock_aggregate

    report = await agent.analyze(context)

    assert 0.0 <= report.positive_score <= 1.0
    assert 0.0 <= report.negative_score <= 1.0
    assert 0.0 <= report.neutral_score <= 1.0
    assert -1.0 <= report.sentiment_score <= 1.0


@pytest.mark.asyncio
async def test_finbert_analyst_sentiment_mapping(sample_context):
    """Test FinBERT analyst correctly maps sentiment."""
    from src.agents.market_intelligence import FinBERTSentimentAnalyst

    agent = FinBERTSentimentAnalyst()

    # Test positive sentiment
    context = {**sample_context, "texts": ["Great news"]}

    def mock_positive(texts):
        return {
            "sentiment": "positive",
            "positive": 0.8,
            "negative": 0.1,
            "neutral": 0.1,
            "confidence": 0.7,
        }

    agent._aggregate_sentiments = mock_positive
    report = await agent.analyze(context)
    assert report.sentiment == Sentiment.BULLISH

    # Test negative sentiment
    def mock_negative(texts):
        return {
            "sentiment": "negative",
            "positive": 0.1,
            "negative": 0.8,
            "neutral": 0.1,
            "confidence": 0.7,
        }

    agent._aggregate_sentiments = mock_negative
    report = await agent.analyze(context)
    assert report.sentiment == Sentiment.BEARISH

    # Test neutral sentiment
    def mock_neutral(texts):
        return {
            "sentiment": "neutral",
            "positive": 0.3,
            "negative": 0.3,
            "neutral": 0.4,
            "confidence": 0.1,
        }

    agent._aggregate_sentiments = mock_neutral
    report = await agent.analyze(context)
    assert report.sentiment == Sentiment.NEUTRAL


@pytest.mark.asyncio
async def test_finbert_analyst_empty_texts(sample_context):
    """Test FinBERT analyst handles empty text list."""
    from src.agents.market_intelligence import FinBERTSentimentAnalyst

    agent = FinBERTSentimentAnalyst()

    context = {**sample_context, "texts": []}

    report = await agent.analyze(context)

    assert isinstance(report, FinBERTSentimentReport)
    assert report.sentiment == Sentiment.NEUTRAL
    assert report.confidence == 0.0


@pytest.mark.asyncio
async def test_finbert_analyst_error_handling(sample_context):
    """Test FinBERT analyst handles errors gracefully."""
    from src.agents.market_intelligence import FinBERTSentimentAnalyst

    agent = FinBERTSentimentAnalyst()

    context = {**sample_context, "texts": ["test"]}

    # Mock to raise an error
    def mock_error(texts):
        raise ValueError("Test error")

    agent._aggregate_sentiments = mock_error

    report = await agent.analyze(context)

    assert isinstance(report, FinBERTSentimentReport)
    assert report.confidence == 0.0
    assert "failed" in report.summary.lower()


# =============================================================================
# FinGPT Generative Analyst Tests
# =============================================================================


@pytest.mark.asyncio
async def test_fingpt_analyst_basic_analysis(sample_context):
    """Test FinGPT analyst produces valid report with mock."""
    from src.agents.market_intelligence import FinGPTGenerativeAnalyst

    agent = FinGPTGenerativeAnalyst(use_local=False)  # Use non-local to avoid loading

    context = {
        **sample_context,
        "text": "Apple reports strong earnings with revenue up 15% YoY",
        "analysis_type": "general_analysis",
    }

    report = await agent.analyze(context)

    assert isinstance(report, FinGPTGenerativeReport)
    assert report.agent_role == AgentRole.FINGPT_GENERATIVE_ANALYST
    assert report.symbol == sample_context["symbol"]
    assert report.analysis_type == "general_analysis"


@pytest.mark.asyncio
async def test_fingpt_analyst_structured_output(sample_context):
    """Test FinGPT analyst produces structured insights."""
    from src.agents.market_intelligence import FinGPTGenerativeAnalyst

    agent = FinGPTGenerativeAnalyst(use_local=False)

    context = {
        **sample_context,
        "text": "Financial text to analyze",
    }

    # Mock the generation
    def mock_generate(prompt, max_length):
        return """Key insights:
1. Strong revenue growth
2. Improved margins
3. Market share expansion

Risks:
1. Competition increasing
2. Supply chain concerns

Opportunities:
1. New product launches
2. Market expansion
"""

    agent._generate_response = mock_generate

    report = await agent.analyze(context)

    assert isinstance(report.key_insights, list)
    assert isinstance(report.risks_identified, list)
    assert isinstance(report.opportunities_identified, list)
    assert len(report.key_insights) > 0


@pytest.mark.asyncio
async def test_fingpt_analyst_analysis_types(sample_context):
    """Test FinGPT analyst handles different analysis types."""
    from src.agents.market_intelligence import FinGPTGenerativeAnalyst

    agent = FinGPTGenerativeAnalyst(use_local=False)

    analysis_types = [
        "summarize_filing",
        "analyze_transcript",
        "analyze_news",
        "general_analysis",
    ]

    for analysis_type in analysis_types:
        context = {
            **sample_context,
            "text": "Test text",
            "analysis_type": analysis_type,
        }

        report = await agent.analyze(context)

        assert report.analysis_type == analysis_type
        assert isinstance(report, FinGPTGenerativeReport)


@pytest.mark.asyncio
async def test_fingpt_analyst_multiple_texts(sample_context):
    """Test FinGPT analyst handles multiple texts."""
    from src.agents.market_intelligence import FinGPTGenerativeAnalyst

    agent = FinGPTGenerativeAnalyst(use_local=False)

    context = {
        **sample_context,
        "texts": ["Text 1", "Text 2", "Text 3"],
    }

    report = await agent.analyze(context)

    assert isinstance(report, FinGPTGenerativeReport)


@pytest.mark.asyncio
async def test_fingpt_analyst_error_handling(sample_context):
    """Test FinGPT analyst handles errors gracefully."""
    from src.agents.market_intelligence import FinGPTGenerativeAnalyst

    agent = FinGPTGenerativeAnalyst(use_local=False)

    context = {**sample_context, "text": "test"}

    # Mock to raise an error
    def mock_error(prompt, max_length):
        raise RuntimeError("Test error")

    agent._generate_response = mock_error

    report = await agent.analyze(context)

    assert isinstance(report, FinGPTGenerativeReport)
    assert report.confidence == 0.0
    assert "failed" in report.summary.lower()


@pytest.mark.asyncio
async def test_fingpt_analyst_confidence_calculation(sample_context):
    """Test FinGPT analyst calculates confidence based on output quality."""
    from src.agents.market_intelligence import FinGPTGenerativeAnalyst

    agent = FinGPTGenerativeAnalyst(use_local=False)

    context = {**sample_context, "text": "test"}

    # Mock rich output
    def mock_rich_output(prompt, max_length):
        return """Insights:
1. Point 1
2. Point 2
3. Point 3
4. Point 4

Risks:
- Risk 1
- Risk 2
- Risk 3

Opportunities:
+ Opportunity 1
+ Opportunity 2
+ Opportunity 3
"""

    agent._generate_response = mock_rich_output

    report = await agent.analyze(context)

    assert report.confidence >= 0.7  # Should have high confidence with rich output
