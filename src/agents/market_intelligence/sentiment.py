"""Market Intelligence Team - Sentiment Analyst."""

import json
from typing import Any

from ...config.prompts import SENTIMENT_ANALYST_PROMPT
from ...data.providers import NewsProvider
from ...data.schemas import AgentRole, Sentiment, SentimentReport
from ...utils import get_logger
from ..base import BaseAgent


logger = get_logger(__name__)


class SentimentAnalyst(BaseAgent):
    """
    Sentiment Analyst agent.

    Gauges market mood by analyzing social media, forums, and news sentiment trends.
    """

    def __init__(self):
        super().__init__(
            role=AgentRole.SENTIMENT_ANALYST,
            system_prompt=SENTIMENT_ANALYST_PROMPT,
            temperature=0.6,
        )
        self.news_provider = NewsProvider()

    async def analyze(self, context: dict[str, Any]) -> SentimentReport:
        """
        Analyze sentiment data for a symbol.

        Args:
            context: Contains 'symbol', optional providers

        Returns:
            SentimentReport with analysis
        """
        symbol = context.get("symbol", "UNKNOWN")

        # Use provided provider or default
        news_provider = context.get("news_provider", self.news_provider)

        logger.info("Starting sentiment analysis", symbol=symbol)

        try:
            # Fetch sentiment data
            news_sentiment = news_provider.get_news_sentiment(symbol, lookback_days=7)
            news_items = news_provider.get_news(symbol, limit=15)

            # Analyze individual news items for trending topics
            topics = []
            for item in news_items:
                # Extract potential topics from titles
                title_words = item["title"].lower().split()
                # Filter out common words and keep meaningful ones
                meaningful_words = [
                    w
                    for w in title_words
                    if len(w) > 4
                    and w not in ["about", "after", "before", "their", "these", "those"]
                ]
                topics.extend(meaningful_words[:2])  # Top 2 words per article

            # Get most common topics
            from collections import Counter

            topic_counts = Counter(topics)
            trending_topics = [topic for topic, _ in topic_counts.most_common(5)]

            # Construct input for LLM
            input_text = f"""
Analyze the sentiment and market mood for {symbol} based on recent news and data.

SENTIMENT DATA:
- Overall News Sentiment: {news_sentiment["sentiment"]}
- Sentiment Score: {news_sentiment["score"]:.2f} (range: -1 to 1)
- News Count (7 days): {news_sentiment["news_count"]}
- Positive Articles: {news_sentiment.get("positive_articles", 0)}
- Negative Articles: {news_sentiment.get("negative_articles", 0)}
- Neutral Articles: {news_sentiment.get("neutral_articles", 0)}

TRENDING TOPICS:
{", ".join(trending_topics) if trending_topics else "No clear trends identified"}

RECENT HEADLINES:
{chr(10).join([f"- {item['title']}" for item in news_items[:5]])}

Please analyze:
1. Overall social/market sentiment (bullish/bearish/neutral)
2. Sentiment score assessment (-1 to 1 scale)
3. Trending topics or themes
4. Retail investor positioning based on news flow
5. Your confidence level (1-10)

Provide your analysis in JSON format:
{{
    "social_sentiment": "bullish" or "bearish" or "neutral",
    "sentiment_score": <-1.0 to 1.0>,
    "trending_topics": ["topic1", "topic2", "topic3"],
    "retail_positioning": "description of retail investor sentiment",
    "key_points": ["point1", "point2", "point3"],
    "confidence_level": <1-10>,
    "analysis_summary": "brief summary"
}}
"""

            # Generate analysis
            response = await self._generate_response(input_text)

            # Parse JSON response
            try:
                # Extract JSON from response
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0].strip()
                else:
                    json_str = response.strip()

                parsed = json.loads(json_str)

                sentiment_str = parsed.get("social_sentiment", "neutral").lower()
                sentiment_score = float(parsed.get("sentiment_score", news_sentiment["score"]))
                trending = parsed.get("trending_topics", trending_topics)
                retail_pos = parsed.get(
                    "retail_positioning", "Mixed sentiment among retail investors"
                )
                key_points = parsed.get("key_points", [])
                confidence_level = parsed.get("confidence_level", 6)
                analysis_summary = parsed.get("analysis_summary", response[:500])

                # Map sentiment
                if sentiment_str in ["bullish", "positive"]:
                    social_sentiment = Sentiment.BULLISH
                elif sentiment_str in ["bearish", "negative"]:
                    social_sentiment = Sentiment.BEARISH
                else:
                    social_sentiment = Sentiment.NEUTRAL

                # Clamp sentiment score
                sentiment_score = max(-1.0, min(1.0, sentiment_score))

            except (json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
                logger.warning("Failed to parse LLM response, using defaults", error=str(e))
                social_sentiment = Sentiment.NEUTRAL
                sentiment_score = news_sentiment["score"]
                trending = trending_topics
                retail_pos = "Unable to determine retail positioning"
                key_points = ["Analysis pending - parsing error"]
                confidence_level = 5
                analysis_summary = response[:500]

            report = SentimentReport(
                symbol=symbol,
                confidence_level=confidence_level,
                analysis=analysis_summary,
                key_points=key_points,
                social_sentiment=social_sentiment,
                sentiment_score=sentiment_score,
                trending_topics=trending,
                retail_positioning=retail_pos,
            )

            logger.info(
                "Sentiment analysis complete",
                symbol=symbol,
                sentiment=social_sentiment.value,
                score=sentiment_score,
                confidence=confidence_level,
            )

            return report

        except Exception as e:
            logger.error("Sentiment analysis failed", symbol=symbol, error=str(e))

            return SentimentReport(
                symbol=symbol,
                confidence_level=1,
                analysis=f"Analysis failed: {str(e)}",
                key_points=["Analysis error occurred"],
                social_sentiment=Sentiment.NEUTRAL,
                sentiment_score=0.0,
                trending_topics=[],
                retail_positioning="Error determining positioning",
            )
