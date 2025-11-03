"""Unit tests for NewsProvider."""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from src.data.providers.news import NewsProvider


class TestNewsProvider:
    """Test suite for NewsProvider."""

    def test_initialization(self):
        """Test provider initialization."""
        provider = NewsProvider()
        assert provider._cache == {}

    def test_analyze_sentiment_positive(self):
        """Test sentiment analysis for positive text."""
        provider = NewsProvider()

        text = "Stock surges on strong earnings beat and positive outlook"
        sentiment = provider._analyze_sentiment(text)

        assert sentiment == "positive"

    def test_analyze_sentiment_negative(self):
        """Test sentiment analysis for negative text."""
        provider = NewsProvider()

        text = "Stock plummets as company misses earnings and faces weak demand"
        sentiment = provider._analyze_sentiment(text)

        assert sentiment == "negative"

    def test_analyze_sentiment_neutral(self):
        """Test sentiment analysis for neutral text."""
        provider = NewsProvider()

        text = "Company announces regular quarterly dividend"
        sentiment = provider._analyze_sentiment(text)

        assert sentiment == "neutral"

    def test_analyze_sentiment_empty(self):
        """Test sentiment analysis for empty text."""
        provider = NewsProvider()

        sentiment = provider._analyze_sentiment("")
        assert sentiment == "neutral"

    def test_analyze_sentiment_mixed(self):
        """Test sentiment analysis for mixed text."""
        provider = NewsProvider()

        # Equal positive and negative keywords
        text = "Strong gains offset by significant risks and concerns"
        sentiment = provider._analyze_sentiment(text)

        # Should be neutral when balanced
        assert sentiment == "neutral"

    @patch("src.data.providers.news.yf.Ticker")
    def test_get_company_news(self, mock_ticker):
        """Test getting company news."""
        mock_news = [
            {
                "title": "Company Reports Strong Earnings",
                "publisher": "Financial Times",
                "link": "https://example.com/article1",
                "providerPublishTime": int(datetime.now().timestamp()),
                "summary": "Revenue beats expectations",
            },
            {
                "title": "New Product Launch Announced",
                "publisher": "Tech News",
                "link": "https://example.com/article2",
                "providerPublishTime": int(datetime.now().timestamp()),
                "summary": "Innovative new product line",
            },
        ]

        mock_instance = Mock()
        mock_instance.news = mock_news
        mock_ticker.return_value = mock_instance

        provider = NewsProvider()
        articles = provider.get_company_news("AAPL", days_back=7, max_articles=20)

        assert len(articles) == 2
        assert articles[0]["title"] == "Company Reports Strong Earnings"
        assert "sentiment" in articles[0]

    @patch("src.data.providers.news.yf.Ticker")
    def test_get_company_news_error(self, mock_ticker):
        """Test company news error handling."""
        mock_ticker.side_effect = Exception("API Error")

        provider = NewsProvider()
        articles = provider.get_company_news("INVALID")

        assert articles == []

    @patch("src.data.providers.news.yf.Ticker")
    def test_get_company_news_max_articles(self, mock_ticker):
        """Test max_articles limit."""
        # Create 30 articles
        mock_news = [
            {
                "title": f"Article {i}",
                "publisher": "Publisher",
                "link": f"https://example.com/article{i}",
                "providerPublishTime": int(datetime.now().timestamp()),
                "summary": f"Summary {i}",
            }
            for i in range(30)
        ]

        mock_instance = Mock()
        mock_instance.news = mock_news
        mock_ticker.return_value = mock_instance

        provider = NewsProvider()
        articles = provider.get_company_news("AAPL", max_articles=10)

        # Should only return 10 articles
        assert len(articles) == 10

    @patch("src.data.providers.news.yf.Ticker")
    def test_get_market_news(self, mock_ticker):
        """Test getting market news."""
        mock_news = [
            {
                "title": "Market Rally Continues",
                "publisher": "Market Watch",
                "link": "https://example.com/market1",
                "providerPublishTime": int(datetime.now().timestamp()),
                "summary": "Indices reach new highs",
            },
        ]

        def mock_ticker_factory(symbol):
            mock_instance = Mock()
            mock_instance.news = mock_news
            return mock_instance

        mock_ticker.side_effect = mock_ticker_factory

        provider = NewsProvider()
        articles = provider.get_market_news(days_back=7, max_articles=20)

        # Should return articles (number depends on mocking)
        assert isinstance(articles, list)

    @patch("src.data.providers.news.yf.Ticker")
    def test_get_market_news_deduplication(self, mock_ticker):
        """Test that market news deduplicates articles."""
        # Same article from multiple sources
        same_article = {
            "title": "Market Rally Continues",
            "publisher": "Market Watch",
            "link": "https://example.com/market1",
            "providerPublishTime": int(datetime.now().timestamp()),
            "summary": "Indices reach new highs",
        }

        def mock_ticker_factory(symbol):
            mock_instance = Mock()
            mock_instance.news = [same_article, same_article]
            return mock_instance

        mock_ticker.side_effect = mock_ticker_factory

        provider = NewsProvider()
        articles = provider.get_market_news()

        # Check for deduplication by title
        titles = [article["title"] for article in articles]
        assert len(titles) == len(set(titles))  # All unique

    @patch("src.data.providers.news.yf.Ticker")
    def test_aggregate_sentiment_bullish(self, mock_ticker):
        """Test aggregate sentiment for bullish news."""
        mock_news = [
            {
                "title": "Strong surge in stock price",
                "publisher": "Publisher",
                "link": "https://example.com/1",
                "providerPublishTime": int(datetime.now().timestamp()),
                "summary": "Excellent growth and profit",
            },
            {
                "title": "Company beats expectations",
                "publisher": "Publisher",
                "link": "https://example.com/2",
                "providerPublishTime": int(datetime.now().timestamp()),
                "summary": "Strong rally continues",
            },
            {
                "title": "Positive outlook announced",
                "publisher": "Publisher",
                "link": "https://example.com/3",
                "providerPublishTime": int(datetime.now().timestamp()),
                "summary": "Bullish sentiment high",
            },
        ]

        mock_instance = Mock()
        mock_instance.news = mock_news
        mock_ticker.return_value = mock_instance

        provider = NewsProvider()
        sentiment = provider.aggregate_sentiment("AAPL", days_back=7)

        assert sentiment["sentiment_label"] == "bullish"
        assert sentiment["sentiment_score"] > 0.2
        assert sentiment["article_count"] == 3
        assert sentiment["positive_count"] > sentiment["negative_count"]

    @patch("src.data.providers.news.yf.Ticker")
    def test_aggregate_sentiment_bearish(self, mock_ticker):
        """Test aggregate sentiment for bearish news."""
        mock_news = [
            {
                "title": "Stock plummets on weak earnings",
                "publisher": "Publisher",
                "link": "https://example.com/1",
                "providerPublishTime": int(datetime.now().timestamp()),
                "summary": "Poor performance and loss",
            },
            {
                "title": "Company faces decline",
                "publisher": "Publisher",
                "link": "https://example.com/2",
                "providerPublishTime": int(datetime.now().timestamp()),
                "summary": "Negative outlook and concerns",
            },
        ]

        mock_instance = Mock()
        mock_instance.news = mock_news
        mock_ticker.return_value = mock_instance

        provider = NewsProvider()
        sentiment = provider.aggregate_sentiment("AAPL", days_back=7)

        assert sentiment["sentiment_label"] == "bearish"
        assert sentiment["sentiment_score"] < -0.2
        assert sentiment["negative_count"] > sentiment["positive_count"]

    @patch("src.data.providers.news.yf.Ticker")
    def test_aggregate_sentiment_neutral(self, mock_ticker):
        """Test aggregate sentiment for neutral news."""
        mock_news = [
            {
                "title": "Company announces dividend",
                "publisher": "Publisher",
                "link": "https://example.com/1",
                "providerPublishTime": int(datetime.now().timestamp()),
                "summary": "Regular quarterly dividend",
            },
        ]

        mock_instance = Mock()
        mock_instance.news = mock_news
        mock_ticker.return_value = mock_instance

        provider = NewsProvider()
        sentiment = provider.aggregate_sentiment("AAPL", days_back=7)

        assert sentiment["sentiment_label"] == "neutral"
        assert -0.2 <= sentiment["sentiment_score"] <= 0.2

    @patch("src.data.providers.news.yf.Ticker")
    def test_aggregate_sentiment_no_articles(self, mock_ticker):
        """Test aggregate sentiment with no articles."""
        mock_instance = Mock()
        mock_instance.news = []
        mock_ticker.return_value = mock_instance

        provider = NewsProvider()
        sentiment = provider.aggregate_sentiment("AAPL", days_back=7)

        assert sentiment["sentiment_score"] == 0.0
        assert sentiment["sentiment_label"] == "neutral"
        assert sentiment["article_count"] == 0

    @patch("src.data.providers.news.yf.Ticker")
    def test_aggregate_sentiment_recent_headlines(self, mock_ticker):
        """Test that aggregate sentiment includes recent headlines."""
        mock_news = [
            {
                "title": f"Headline {i}",
                "publisher": "Publisher",
                "link": f"https://example.com/{i}",
                "providerPublishTime": int(datetime.now().timestamp()),
                "summary": "Summary",
            }
            for i in range(10)
        ]

        mock_instance = Mock()
        mock_instance.news = mock_news
        mock_ticker.return_value = mock_instance

        provider = NewsProvider()
        sentiment = provider.aggregate_sentiment("AAPL")

        assert "recent_headlines" in sentiment
        assert len(sentiment["recent_headlines"]) == 5  # Top 5

    def test_get_economic_calendar(self):
        """Test getting economic calendar."""
        provider = NewsProvider()
        events = provider.get_economic_calendar(days_ahead=7)

        # Should return list of events
        assert isinstance(events, list)

        # Each event should have required fields
        for event in events:
            assert "name" in event
            assert "date" in event
            assert "importance" in event
            assert "description" in event

    def test_get_economic_calendar_date_filtering(self):
        """Test economic calendar filters by date range."""
        provider = NewsProvider()

        # Request events for next 7 days
        events_7 = provider.get_economic_calendar(days_ahead=7)

        # Request events for next 30 days
        events_30 = provider.get_economic_calendar(days_ahead=30)

        # 30-day window should have at least as many events as 7-day
        assert len(events_30) >= len(events_7)

        # All events should be in the future
        today = datetime.now()
        for event in events_7:
            assert event["date"] >= today
            assert event["date"] <= today + timedelta(days=7)


class TestNewsProviderIntegration:
    """Integration-style tests."""

    @pytest.mark.skip(reason="Integration test - requires network")
    def test_real_api_call(self):
        """Test with real API call (requires network)."""
        provider = NewsProvider()

        # Get news for a major stock
        articles = provider.get_company_news("AAPL", days_back=7, max_articles=5)

        # Should return some articles
        assert isinstance(articles, list)
        # May be empty if API is down or rate-limited
