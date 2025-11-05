"""Strategy & Research Team - Bullish Researcher."""

import json
from typing import Any

from ...config.prompts import BULLISH_RESEARCHER_PROMPT
from ...data.schemas import AgentRole, DebateArgument, Sentiment
from ...utils import get_logger
from ..base import BaseAgent


logger = get_logger(__name__)


class BullishResearcher(BaseAgent):
    """
    Bullish Researcher agent.

    Constructs the strongest possible argument for taking long positions
    based on analyst reports.
    """

    def __init__(self):
        super().__init__(
            role=AgentRole.BULLISH_RESEARCHER,
            system_prompt=BULLISH_RESEARCHER_PROMPT,
            temperature=0.7,  # Higher temperature for creative argumentation
        )

    async def debate(
        self,
        context: dict[str, Any],
        round_number: int,
        previous_arguments: list[DebateArgument] = None,
    ) -> DebateArgument:
        """
        Make a bullish argument in the debate.

        Args:
            context: Contains analyst reports and symbol
            round_number: Current debate round
            previous_arguments: Arguments from previous rounds

        Returns:
            DebateArgument with bullish position
        """
        symbol = context.get("symbol", "UNKNOWN")
        analyst_reports = context.get("analyst_reports", {})

        logger.info("Bullish researcher debating", symbol=symbol, round=round_number)

        # Extract key information from analyst reports
        fundamentals = analyst_reports.get("fundamentals")
        macro_news = analyst_reports.get("macro_news")
        sentiment = analyst_reports.get("sentiment")
        technical = analyst_reports.get("technical")

        # Build context for this round
        if round_number == 1:
            # First round - build initial case
            input_text = f"""
Construct a strong BULLISH argument for {symbol} based on the following analyst reports:

FUNDAMENTALS:
- Investment Thesis: {fundamentals.investment_thesis.value if fundamentals else "N/A"}
- Intrinsic Value: ${fundamentals.intrinsic_value if fundamentals and fundamentals.intrinsic_value else "N/A"}
- Key Points: {", ".join(fundamentals.key_points if fundamentals else [])}
- Confidence: {fundamentals.confidence_level if fundamentals else 0}/10

MACRO & NEWS:
- Market Sentiment: {macro_news.market_sentiment.value if macro_news else "N/A"}
- Key Themes: {", ".join(macro_news.macro_themes if macro_news else [])}
- Confidence: {macro_news.confidence_level if macro_news else 0}/10

SENTIMENT:
- Social Sentiment: {sentiment.social_sentiment.value if sentiment else "N/A"}
- Score: {sentiment.sentiment_score if sentiment else 0:.2f}
- Trending: {", ".join(sentiment.trending_topics if sentiment else [])}
- Confidence: {sentiment.confidence_level if sentiment else 0}/10

TECHNICAL:
- Trend: {technical.trend_direction.value if technical else "N/A"}
- Support: {", ".join([f"${x:.2f}" for x in (technical.support_levels if technical else [])])}
- Resistance: {", ".join([f"${x:.2f}" for x in (technical.resistance_levels if technical else [])])}
- Patterns: {", ".join(technical.chart_patterns if technical else [])}
- Confidence: {technical.confidence_level if technical else 0}/10

Build your BULLISH case with:
1. Investment thesis summary (why this is a buying opportunity)
2. Key supporting evidence from each analyst
3. Catalysts that could drive price higher
4. Proposed strategy (buy stock, call options, bull spreads)
5. Acknowledgment of risks but why they're manageable

Provide your argument in JSON format:
{{
    "thesis_summary": "brief bullish thesis",
    "supporting_evidence": ["evidence1", "evidence2", "evidence3"],
    "catalysts": ["catalyst1", "catalyst2"],
    "proposed_strategy": "description of trade",
    "risk_acknowledgment": ["risk1", "risk2"],
    "conviction_level": <1-10>,
    "argument_text": "full argument text"
}}
"""
        else:
            # Subsequent rounds - respond to bearish counterarguments
            bearish_args = [arg for arg in previous_arguments if arg.position == Sentiment.BEARISH]
            latest_bearish = bearish_args[-1] if bearish_args else None

            input_text = f"""
This is debate round {round_number} for {symbol}.

PREVIOUS BEARISH ARGUMENT:
{latest_bearish.argument if latest_bearish else "No bearish argument yet"}

COUNTER these bearish points while strengthening your BULLISH case:

Respond with a rebuttal that:
1. Directly addresses the bearish concerns
2. Provides additional evidence supporting your bullish view
3. Highlights what the bears are missing
4. Reinforces why this is still a buying opportunity

Provide your counter-argument in JSON format:
{{
    "counterpoints": ["counter1", "counter2", "counter3"],
    "additional_evidence": ["evidence1", "evidence2"],
    "bearish_mistakes": ["what bears missed1", "what bears missed2"],
    "conviction_level": <1-10>,
    "argument_text": "full counter-argument text"
}}
"""

        try:
            # Generate argument
            response = await self._generate_response(input_text)

            # Parse JSON response
            try:
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0].strip()
                else:
                    json_str = response.strip()

                parsed = json.loads(json_str)

                if round_number == 1:
                    supporting_evidence = parsed.get("supporting_evidence", [])
                    counterpoints = []
                else:
                    supporting_evidence = parsed.get("additional_evidence", [])
                    counterpoints = parsed.get("counterpoints", [])

                conviction = parsed.get("conviction_level", 7)
                argument_text = parsed.get("argument_text", response[:500])

            except (json.JSONDecodeError, KeyError, IndexError) as e:
                logger.warning("Failed to parse response, using full text", error=str(e))
                supporting_evidence = ["See full argument"]
                counterpoints = []
                conviction = 7
                argument_text = response

            argument = DebateArgument(
                round_number=round_number,
                role=AgentRole.BULLISH_RESEARCHER,
                position=Sentiment.BULLISH,
                argument=argument_text,
                supporting_evidence=supporting_evidence,
                counterpoints=counterpoints,
            )

            logger.info(
                "Bullish argument complete",
                symbol=symbol,
                round=round_number,
                conviction=conviction,
            )

            return argument

        except Exception as e:
            logger.error("Bullish debate failed", symbol=symbol, round=round_number, error=str(e))

            return DebateArgument(
                round_number=round_number,
                role=AgentRole.BULLISH_RESEARCHER,
                position=Sentiment.BULLISH,
                argument=f"Error generating argument: {str(e)}",
                supporting_evidence=[],
                counterpoints=[],
            )
