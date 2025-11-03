"""News provider using yfinance and keyword-based sentiment analysis."""

from datetime import datetime, timedelta
from typing import Any

import yfinance as yf

from src.utils.logger import get_logger


logger = get_logger(__name__)


class NewsProvider:
    """Provider for news and sentiment analysis."""

    # Keyword lists for sentiment analysis
    POSITIVE_KEYWORDS = [
        "surge",
        "rally",
        "gain",
        "profit",
        "beat",
        "strong",
        "growth",
        "positive",
        "bullish",
        "upside",
        "outperform",
        "upgrade",
        "excellent",
        "success",
        "record",
        "breakthrough",
        "innovation",
        "expand",
        "increase",
    ]

    NEGATIVE_KEYWORDS = [
        "plummet",
        "fall",
        "loss",
        "miss",
        "weak",
        "decline",
        "negative",
        "bearish",
        "downside",
        "underperform",
        "downgrade",
        "poor",
        "concern",
        "risk",
        "uncertainty",
        "cut",
        "reduce",
        "problem",
        "crisis",
    ]

    def __init__(self):
        """Initialize the news provider."""
        self._cache: dict[str, Any] = {}
        logger.info("NewsProvider initialized")

    def _analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of text using keyword matching.

        Args:
            text: Text to analyze

        Returns:
            Sentiment label: "positive", "negative", or "neutral"
        """
        if not text:
            return "neutral"

        text_lower = text.lower()

        # Count positive and negative keywords
        positive_count = sum(1 for word in self.POSITIVE_KEYWORDS if word in text_lower)
        negative_count = sum(1 for word in self.NEGATIVE_KEYWORDS if word in text_lower)

        # Determine sentiment
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def get_company_news(
        self, symbol: str, days_back: int = 7, max_articles: int = 20
    ) -> list[dict[str, Any]]:
        """
        Get news articles for a company.

        Args:
            symbol: Stock symbol
            days_back: Number of days to look back
            max_articles: Maximum number of articles to return

        Returns:
            List of news articles with sentiment
        """
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news

            if not news:
                logger.warning("No news found", symbol=symbol)
                return []

            # Filter by date
            cutoff_time = datetime.now() - timedelta(days=days_back)
            cutoff_timestamp = int(cutoff_time.timestamp())

            articles = []
            for article in news[:max_articles]:
                publish_time = article.get("providerPublishTime", 0)

                if publish_time >= cutoff_timestamp:
                    # Add sentiment analysis
                    title = article.get("title", "")
                    summary = article.get("summary", "")
                    combined_text = f"{title} {summary}"

                    processed_article = {
                        "title": title,
                        "publisher": article.get("publisher", "Unknown"),
                        "link": article.get("link", ""),
                        "published": datetime.fromtimestamp(publish_time),
                        "summary": summary,
                        "sentiment": self._analyze_sentiment(combined_text),
                    }
                    articles.append(processed_article)

            logger.info(
                "Retrieved company news",
                symbol=symbol,
                articles=len(articles),
                days_back=days_back,
            )
            return articles

        except Exception as e:
            logger.error("Failed to get company news", symbol=symbol, error=str(e))
            return []

    def get_market_news(self, days_back: int = 7, max_articles: int = 20) -> list[dict[str, Any]]:
        """
        Get general market news.

        Args:
            days_back: Number of days to look back
            max_articles: Maximum number of articles to return

        Returns:
            List of news articles with sentiment
        """
        try:
            # Get news from major indices
            indices = ["^GSPC", "^DJI", "^IXIC"]
            all_articles = []
            seen_titles = set()

            for index_symbol in indices:
                try:
                    ticker = yf.Ticker(index_symbol)
                    news = ticker.news

                    if not news:
                        continue

                    cutoff_time = datetime.now() - timedelta(days=days_back)
                    cutoff_timestamp = int(cutoff_time.timestamp())

                    for article in news:
                        publish_time = article.get("providerPublishTime", 0)
                        title = article.get("title", "")

                        # Deduplicate by title
                        if publish_time >= cutoff_timestamp and title not in seen_titles:
                            seen_titles.add(title)

                            summary = article.get("summary", "")
                            combined_text = f"{title} {summary}"

                            processed_article = {
                                "title": title,
                                "publisher": article.get("publisher", "Unknown"),
                                "link": article.get("link", ""),
                                "published": datetime.fromtimestamp(publish_time),
                                "summary": summary,
                                "sentiment": self._analyze_sentiment(combined_text),
                            }
                            all_articles.append(processed_article)

                except Exception:
                    continue

            # Sort by date and limit
            all_articles.sort(key=lambda x: x["published"], reverse=True)
            articles = all_articles[:max_articles]

            logger.info(
                "Retrieved market news",
                articles=len(articles),
                days_back=days_back,
            )
            return articles

        except Exception as e:
            logger.error("Failed to get market news", error=str(e))
            return []

    def aggregate_sentiment(self, symbol: str, days_back: int = 7) -> dict[str, Any]:
        """
        Aggregate sentiment from recent news.

        Args:
            symbol: Stock symbol
            days_back: Number of days to look back

        Returns:
            Dictionary with aggregated sentiment metrics
        """
        try:
            articles = self.get_company_news(symbol, days_back=days_back)

            if not articles:
                return {
                    "sentiment_score": 0.0,
                    "sentiment_label": "neutral",
                    "article_count": 0,
                    "positive_count": 0,
                    "negative_count": 0,
                    "neutral_count": 0,
                    "recent_headlines": [],
                }

            # Count sentiments
            positive_count = sum(1 for a in articles if a["sentiment"] == "positive")
            negative_count = sum(1 for a in articles if a["sentiment"] == "negative")
            neutral_count = sum(1 for a in articles if a["sentiment"] == "neutral")

            # Calculate sentiment score (-1 to +1)
            total = len(articles)
            sentiment_score = (positive_count - negative_count) / total

            # Determine label
            if sentiment_score > 0.2:
                sentiment_label = "bullish"
            elif sentiment_score < -0.2:
                sentiment_label = "bearish"
            else:
                sentiment_label = "neutral"

            # Get recent headlines
            recent_headlines = [a["title"] for a in articles[:5]]

            result = {
                "sentiment_score": sentiment_score,
                "sentiment_label": sentiment_label,
                "article_count": total,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count,
                "recent_headlines": recent_headlines,
            }

            logger.info(
                "Aggregated sentiment",
                symbol=symbol,
                label=sentiment_label,
                score=sentiment_score,
            )
            return result

        except Exception as e:
            logger.error("Failed to aggregate sentiment", symbol=symbol, error=str(e))
            return {
                "sentiment_score": 0.0,
                "sentiment_label": "neutral",
                "article_count": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "recent_headlines": [],
            }

    def get_economic_calendar(self, days_ahead: int = 7) -> list[dict[str, Any]]:
        """
        Get upcoming economic events (simplified placeholder).

        Args:
            days_ahead: Number of days to look ahead

        Returns:
            List of economic events
        """
        # This is a simplified implementation
        # In production, you would integrate with an economic calendar API
        today = datetime.now()
        end_date = today + timedelta(days=days_ahead)

        # Placeholder events (in production, fetch from API)
        events = []

        # Add sample weekly events within the date range
        current_date = today
        while current_date <= end_date:
            # Weekly unemployment claims (Thursdays)
            if current_date.weekday() == 3:  # Thursday
                events.append(
                    {
                        "name": "Initial Jobless Claims",
                        "date": current_date,
                        "importance": "medium",
                        "description": "Weekly unemployment insurance claims",
                    }
                )

            # Monthly CPI (mid-month)
            if current_date.day == 15:
                events.append(
                    {
                        "name": "Consumer Price Index (CPI)",
                        "date": current_date,
                        "importance": "high",
                        "description": "Monthly inflation data",
                    }
                )

            # Monthly jobs report (first Friday)
            if current_date.weekday() == 4 and 1 <= current_date.day <= 7:
                events.append(
                    {
                        "name": "Non-Farm Payrolls",
                        "date": current_date,
                        "importance": "high",
                        "description": "Monthly employment report",
                    }
                )

            # FOMC meetings (quarterly, approximate)
            if current_date.day in [15, 16] and current_date.month in [3, 6, 9, 12]:
                events.append(
                    {
                        "name": "FOMC Meeting",
                        "date": current_date,
                        "importance": "high",
                        "description": "Federal Reserve monetary policy meeting",
                    }
                )

            current_date += timedelta(days=1)

        logger.info("Generated economic calendar", events=len(events), days_ahead=days_ahead)
        return events
