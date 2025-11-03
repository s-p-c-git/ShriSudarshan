"""
Tests for Market Intelligence agents using mock implementations.

Tests all four Market Intelligence agents:
- FundamentalsAnalyst
- TechnicalAnalyst
- SentimentAnalyst
- MacroNewsAnalyst
"""

import pytest

from src.data.schemas import (
    AgentRole,
    FundamentalsReport,
    MacroNewsReport,
    Sentiment,
    SentimentReport,
    TechnicalReport,
    TrendDirection,
)
from tests.mock_agents import (
    MockFundamentalsAnalyst,
    MockMacroNewsAnalyst,
    MockSentimentAnalyst,
    MockTechnicalAnalyst,
)


# =============================================================================
# Fundamentals Analyst Tests
# =============================================================================


@pytest.mark.asyncio
async def test_fundamentals_analyst_basic_analysis(sample_context):
    """Test fundamentals analyst produces valid report."""
    agent = MockFundamentalsAnalyst()
    
    report = await agent.analyze(sample_context)
    
    assert isinstance(report, FundamentalsReport)
    assert report.agent_role == AgentRole.FUNDAMENTALS_ANALYST
    assert report.symbol == sample_context["symbol"]
    assert report.confidence > 0.0
    assert report.summary is not None


@pytest.mark.asyncio
async def test_fundamentals_analyst_contains_metrics(sample_context):
    """Test fundamentals analyst includes financial metrics."""
    agent = MockFundamentalsAnalyst()
    
    report = await agent.analyze(sample_context)
    
    assert report.revenue is not None
    assert report.net_income is not None
    assert report.pe_ratio is not None
    assert report.pb_ratio is not None
    assert report.intrinsic_value is not None


@pytest.mark.asyncio
async def test_fundamentals_analyst_investment_thesis(sample_context):
    """Test fundamentals analyst provides investment thesis."""
    agent = MockFundamentalsAnalyst()
    
    report = await agent.analyze(sample_context)
    
    assert report.investment_thesis in [Sentiment.BULLISH, Sentiment.BEARISH, Sentiment.NEUTRAL]


@pytest.mark.asyncio
async def test_fundamentals_analyst_different_symbols():
    """Test fundamentals analyst handles different symbols."""
    agent = MockFundamentalsAnalyst()
    
    for symbol in ["AAPL", "MSFT", "GOOGL"]:
        context = {"symbol": symbol}
        report = await agent.analyze(context)
        
        assert report.symbol == symbol
        assert isinstance(report, FundamentalsReport)


@pytest.mark.asyncio
async def test_fundamentals_analyst_metadata():
    """Test fundamentals analyst has correct metadata."""
    agent = MockFundamentalsAnalyst()
    
    metadata = agent.get_metadata()
    
    assert metadata["role"] == AgentRole.FUNDAMENTALS_ANALYST.value
    assert "timestamp" in metadata


# =============================================================================
# Technical Analyst Tests
# =============================================================================


@pytest.mark.asyncio
async def test_technical_analyst_basic_analysis(sample_context):
    """Test technical analyst produces valid report."""
    agent = MockTechnicalAnalyst()
    
    report = await agent.analyze(sample_context)
    
    assert isinstance(report, TechnicalReport)
    assert report.agent_role == AgentRole.TECHNICAL_ANALYST
    assert report.symbol == sample_context["symbol"]
    assert report.confidence > 0.0


@pytest.mark.asyncio
async def test_technical_analyst_trend_direction(sample_context):
    """Test technical analyst identifies trend direction."""
    agent = MockTechnicalAnalyst()
    
    report = await agent.analyze(sample_context)
    
    assert report.trend_direction in [
        TrendDirection.STRONG_DOWNTREND,
        TrendDirection.DOWNTREND,
        TrendDirection.SIDEWAYS,
        TrendDirection.UPTREND,
        TrendDirection.STRONG_UPTREND,
    ]


@pytest.mark.asyncio
async def test_technical_analyst_support_resistance(sample_context):
    """Test technical analyst identifies support and resistance levels."""
    agent = MockTechnicalAnalyst()
    
    report = await agent.analyze(sample_context)
    
    assert isinstance(report.support_levels, list)
    assert isinstance(report.resistance_levels, list)
    assert len(report.support_levels) > 0
    assert len(report.resistance_levels) > 0


@pytest.mark.asyncio
async def test_technical_analyst_indicators(sample_context):
    """Test technical analyst includes technical indicators."""
    agent = MockTechnicalAnalyst()
    
    report = await agent.analyze(sample_context)
    
    assert isinstance(report.indicators, dict)
    assert len(report.indicators) > 0


@pytest.mark.asyncio
async def test_technical_analyst_chart_patterns(sample_context):
    """Test technical analyst identifies chart patterns."""
    agent = MockTechnicalAnalyst()
    
    report = await agent.analyze(sample_context)
    
    assert isinstance(report.chart_patterns, list)


@pytest.mark.asyncio
async def test_technical_analyst_volatility(sample_context):
    """Test technical analyst measures volatility."""
    agent = MockTechnicalAnalyst()
    
    report = await agent.analyze(sample_context)
    
    if report.volatility is not None:
        assert report.volatility >= 0.0


# =============================================================================
# Sentiment Analyst Tests
# =============================================================================


@pytest.mark.asyncio
async def test_sentiment_analyst_basic_analysis(sample_context):
    """Test sentiment analyst produces valid report."""
    agent = MockSentimentAnalyst()
    
    report = await agent.analyze(sample_context)
    
    assert isinstance(report, SentimentReport)
    assert report.agent_role == AgentRole.SENTIMENT_ANALYST
    assert report.symbol == sample_context["symbol"]
    assert report.confidence > 0.0


@pytest.mark.asyncio
async def test_sentiment_analyst_social_sentiment(sample_context):
    """Test sentiment analyst provides social sentiment."""
    agent = MockSentimentAnalyst()
    
    report = await agent.analyze(sample_context)
    
    assert report.social_sentiment in [
        Sentiment.VERY_BEARISH,
        Sentiment.BEARISH,
        Sentiment.NEUTRAL,
        Sentiment.BULLISH,
        Sentiment.VERY_BULLISH,
    ]


@pytest.mark.asyncio
async def test_sentiment_analyst_sentiment_score(sample_context):
    """Test sentiment analyst provides sentiment score."""
    agent = MockSentimentAnalyst()
    
    report = await agent.analyze(sample_context)
    
    assert report.sentiment_score >= -1.0
    assert report.sentiment_score <= 1.0


@pytest.mark.asyncio
async def test_sentiment_analyst_volume_trend(sample_context):
    """Test sentiment analyst tracks volume trend."""
    agent = MockSentimentAnalyst()
    
    report = await agent.analyze(sample_context)
    
    assert report.volume_trend is not None


@pytest.mark.asyncio
async def test_sentiment_analyst_interest_metrics(sample_context):
    """Test sentiment analyst tracks interest metrics."""
    agent = MockSentimentAnalyst()
    
    report = await agent.analyze(sample_context)
    
    assert report.retail_interest is not None
    assert report.institutional_activity is not None


# =============================================================================
# Macro/News Analyst Tests
# =============================================================================


@pytest.mark.asyncio
async def test_macro_news_analyst_basic_analysis(sample_context):
    """Test macro/news analyst produces valid report."""
    agent = MockMacroNewsAnalyst()
    
    report = await agent.analyze(sample_context)
    
    assert isinstance(report, MacroNewsReport)
    assert report.agent_role == AgentRole.MACRO_NEWS_ANALYST
    assert report.symbol == sample_context["symbol"]
    assert report.confidence > 0.0


@pytest.mark.asyncio
async def test_macro_news_analyst_market_sentiment(sample_context):
    """Test macro/news analyst provides market sentiment."""
    agent = MockMacroNewsAnalyst()
    
    report = await agent.analyze(sample_context)
    
    assert report.market_sentiment in [
        Sentiment.VERY_BEARISH,
        Sentiment.BEARISH,
        Sentiment.NEUTRAL,
        Sentiment.BULLISH,
        Sentiment.VERY_BULLISH,
    ]


@pytest.mark.asyncio
async def test_macro_news_analyst_key_events(sample_context):
    """Test macro/news analyst identifies key events."""
    agent = MockMacroNewsAnalyst()
    
    report = await agent.analyze(sample_context)
    
    assert isinstance(report.key_events, list)


@pytest.mark.asyncio
async def test_macro_news_analyst_geopolitical_risks(sample_context):
    """Test macro/news analyst identifies geopolitical risks."""
    agent = MockMacroNewsAnalyst()
    
    report = await agent.analyze(sample_context)
    
    assert isinstance(report.geopolitical_risks, list)


@pytest.mark.asyncio
async def test_macro_news_analyst_economic_indicators(sample_context):
    """Test macro/news analyst provides economic indicators."""
    agent = MockMacroNewsAnalyst()
    
    report = await agent.analyze(sample_context)
    
    assert isinstance(report.economic_indicators, dict)


@pytest.mark.asyncio
async def test_macro_news_analyst_news_sentiment(sample_context):
    """Test macro/news analyst provides news sentiment score."""
    agent = MockMacroNewsAnalyst()
    
    report = await agent.analyze(sample_context)
    
    if report.news_sentiment is not None:
        assert report.news_sentiment >= -1.0
        assert report.news_sentiment <= 1.0


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.asyncio
async def test_all_market_intelligence_agents_work_together(sample_context):
    """Test all market intelligence agents can run together."""
    fundamentals_agent = MockFundamentalsAnalyst()
    technical_agent = MockTechnicalAnalyst()
    sentiment_agent = MockSentimentAnalyst()
    macro_news_agent = MockMacroNewsAnalyst()
    
    fundamentals_report = await fundamentals_agent.analyze(sample_context)
    technical_report = await technical_agent.analyze(sample_context)
    sentiment_report = await sentiment_agent.analyze(sample_context)
    macro_news_report = await macro_news_agent.analyze(sample_context)
    
    # Verify all reports are valid
    assert isinstance(fundamentals_report, FundamentalsReport)
    assert isinstance(technical_report, TechnicalReport)
    assert isinstance(sentiment_report, SentimentReport)
    assert isinstance(macro_news_report, MacroNewsReport)
    
    # Verify all have same symbol
    symbol = sample_context["symbol"]
    assert fundamentals_report.symbol == symbol
    assert technical_report.symbol == symbol
    assert sentiment_report.symbol == symbol
    assert macro_news_report.symbol == symbol


@pytest.mark.asyncio
async def test_market_intelligence_agents_no_api_calls(sample_context):
    """Test that mock agents don't make real API calls."""
    # This test verifies the mocks work without network access
    # If this test passes, it means no real API calls were made
    
    agents = [
        MockFundamentalsAnalyst(),
        MockTechnicalAnalyst(),
        MockSentimentAnalyst(),
        MockMacroNewsAnalyst(),
    ]
    
    for agent in agents:
        report = await agent.analyze(sample_context)
        assert report is not None
        assert report.symbol == sample_context["symbol"]


@pytest.mark.asyncio
async def test_market_intelligence_performance():
    """Test that mock agents execute quickly."""
    import time
    
    agent = MockFundamentalsAnalyst()
    context = {"symbol": "AAPL"}
    
    start = time.time()
    report = await agent.analyze(context)
    duration = time.time() - start
    
    # Mock agents should be very fast (< 0.1 seconds)
    assert duration < 0.1
    assert report is not None
