"""Market Intelligence Team - Macro & News Analyst."""

import json
from typing import Any

from ...config.prompts import MACRO_NEWS_ANALYST_PROMPT
from ...data.providers import MarketDataProvider, NewsProvider
from ...data.schemas import AgentRole, MacroNewsReport, Sentiment
from ...utils import get_logger
from ..base import BaseAgent


logger = get_logger(__name__)


class MacroNewsAnalyst(BaseAgent):
    """
    Macro & News Analyst agent.

    Monitors macroeconomic data, central bank policies, geopolitical events,
    and breaking news to provide top-down market view.
    """

    def __init__(self):
        super().__init__(
            role=AgentRole.MACRO_NEWS_ANALYST,
            system_prompt=MACRO_NEWS_ANALYST_PROMPT,
            temperature=0.6,
        )
        self.market_data_provider = MarketDataProvider()
        self.news_provider = NewsProvider()

    async def analyze(self, context: dict[str, Any]) -> MacroNewsReport:
        """
        Analyze macro and news data for a symbol.

        Args:
            context: Contains 'symbol', optional providers

        Returns:
            MacroNewsReport with analysis
        """
        symbol = context.get("symbol", "UNKNOWN")

        # Use provided providers or defaults
        news_provider = context.get("news_provider", self.news_provider)

        logger.info("Starting macro & news analysis", symbol=symbol)

        try:
            # Fetch news data
            news_items = news_provider.get_news(symbol, limit=20)
            news_sentiment = news_provider.get_news_sentiment(symbol, lookback_days=7)

            # Format news for LLM
            news_text = "\n".join(
                [
                    f"- [{item['published'].strftime('%Y-%m-%d')}] {item['title']} ({item['publisher']})"
                    for item in news_items[:10]
                ]
            )

            # Construct input for LLM
            input_text = f"""
Analyze the macroeconomic context and recent news for {symbol}.

RECENT NEWS (Past 7 Days):
{news_text if news_text else "No recent news available"}

NEWS SENTIMENT ANALYSIS:
- Overall Sentiment: {news_sentiment["sentiment"]}
- Sentiment Score: {news_sentiment["score"]:.2f}
- Positive Articles: {news_sentiment.get("positive_articles", 0)}
- Negative Articles: {news_sentiment.get("negative_articles", 0)}
- Neutral Articles: {news_sentiment.get("neutral_articles", 0)}

Please analyze:
1. Key macro themes affecting this stock and its sector
2. Top news items and their potential market impact
3. Overall market sentiment direction
4. Risk events on the horizon
5. Your confidence level (1-10)

Provide your analysis in the following JSON format:
{{
    "macro_themes": ["theme1", "theme2", "theme3"],
    "key_news_items": [
        {{"title": "news title", "impact": "positive/negative/neutral", "significance": "high/medium/low"}},
        ...
    ],
    "market_sentiment": "bullish" or "bearish" or "neutral",
    "risk_events": ["event1", "event2"],
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

                macro_themes = parsed.get("macro_themes", [])
                key_news = parsed.get("key_news_items", [])
                sentiment_str = parsed.get("market_sentiment", "neutral").lower()
                risk_events = parsed.get("risk_events", [])
                key_points = parsed.get("key_points", [])
                confidence_level = parsed.get("confidence_level", 5)
                analysis_summary = parsed.get("analysis_summary", response[:500])

                # Map sentiment
                if sentiment_str in ["bullish", "positive"]:
                    market_sentiment = Sentiment.BULLISH
                elif sentiment_str in ["bearish", "negative"]:
                    market_sentiment = Sentiment.BEARISH
                else:
                    market_sentiment = Sentiment.NEUTRAL

            except (json.JSONDecodeError, KeyError, IndexError) as e:
                logger.warning("Failed to parse LLM response, using defaults", error=str(e))
                macro_themes = ["Analysis pending - parsing error"]
                key_news = []
                market_sentiment = Sentiment.NEUTRAL
                risk_events = []
                key_points = ["Unable to parse detailed analysis"]
                confidence_level = 5
                analysis_summary = response[:500]

            report = MacroNewsReport(
                symbol=symbol,
                confidence_level=confidence_level,
                analysis=analysis_summary,
                key_points=key_points,
                macro_themes=macro_themes,
                news_items=key_news,
                market_sentiment=market_sentiment,
                risk_events=risk_events,
            )

            logger.info(
                "Macro & news analysis complete",
                symbol=symbol,
                sentiment=market_sentiment.value,
                confidence=confidence_level,
            )

            return report

        except Exception as e:
            logger.error("Macro & news analysis failed", symbol=symbol, error=str(e))

            return MacroNewsReport(
                symbol=symbol,
                confidence_level=1,
                analysis=f"Analysis failed: {str(e)}",
                key_points=["Analysis error occurred"],
                macro_themes=[],
                news_items=[],
                market_sentiment=Sentiment.NEUTRAL,
                risk_events=[],
            )
