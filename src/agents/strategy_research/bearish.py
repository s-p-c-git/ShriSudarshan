"""Strategy & Research Team - Bearish Researcher."""

import json
from typing import Any

from ...config.prompts import BEARISH_RESEARCHER_PROMPT
from ...data.schemas import AgentRole, DebateArgument, Sentiment
from ...utils import get_logger
from ..base import BaseAgent


logger = get_logger(__name__)


class BearishResearcher(BaseAgent):
    """
    Bearish Researcher agent.

    Constructs the strongest possible argument for taking short positions
    or avoiding the asset based on analyst reports.
    """

    def __init__(self):
        super().__init__(
            role=AgentRole.BEARISH_RESEARCHER,
            system_prompt=BEARISH_RESEARCHER_PROMPT,
            temperature=0.7,  # Higher temperature for creative argumentation
        )

    async def debate(
        self,
        context: dict[str, Any],
        round_number: int,
        previous_arguments: list[DebateArgument] = None,
    ) -> DebateArgument:
        """
        Make a bearish argument in the debate.

        Args:
            context: Contains analyst reports and symbol
            round_number: Current debate round
            previous_arguments: Arguments from previous rounds

        Returns:
            DebateArgument with bearish position
        """
        symbol = context.get("symbol", "UNKNOWN")
        analyst_reports = context.get("analyst_reports", {})

        logger.info("Bearish researcher debating", symbol=symbol, round=round_number)

        # Extract key information from analyst reports
        fundamentals = analyst_reports.get("fundamentals")
        macro_news = analyst_reports.get("macro_news")
        sentiment = analyst_reports.get("sentiment")
        technical = analyst_reports.get("technical")

        # Build context for this round
        if round_number == 1:
            # First round - build initial case
            input_text = f"""
Construct a strong BEARISH argument for {symbol} based on the following analyst reports:

FUNDAMENTALS:
- Investment Thesis: {fundamentals.investment_thesis.value if fundamentals else 'N/A'}
- Risk Factors: {', '.join(fundamentals.risk_factors if fundamentals else [])}
- Key Points: {', '.join(fundamentals.key_points if fundamentals else [])}
- Confidence: {fundamentals.confidence_level if fundamentals else 0}/10

MACRO & NEWS:
- Market Sentiment: {macro_news.market_sentiment.value if macro_news else 'N/A'}
- Risk Events: {', '.join(macro_news.risk_events if macro_news else [])}
- Key Themes: {', '.join(macro_news.macro_themes if macro_news else [])}
- Confidence: {macro_news.confidence_level if macro_news else 0}/10

SENTIMENT:
- Social Sentiment: {sentiment.social_sentiment.value if sentiment else 'N/A'}
- Score: {sentiment.sentiment_score if sentiment else 0:.2f}
- Retail Positioning: {sentiment.retail_positioning if sentiment else 'N/A'}
- Confidence: {sentiment.confidence_level if sentiment else 0}/10

TECHNICAL:
- Trend: {technical.trend_direction.value if technical else 'N/A'}
- Resistance: {', '.join([f'${x:.2f}' for x in (technical.resistance_levels if technical else [])])}
- Patterns: {', '.join(technical.chart_patterns if technical else [])}
- Confidence: {technical.confidence_level if technical else 0}/10

Build your BEARISH case with:
1. Bearish thesis summary (why this should be avoided or shorted)
2. Key risks and concerns from each analyst
3. Negative catalysts that could drive price lower
4. Proposed strategy (avoid, short stock, put options, bear spreads)
5. Counter-arguments to any bullish points

Provide your argument in JSON format:
{{
    "thesis_summary": "brief bearish thesis",
    "risks_and_concerns": ["risk1", "risk2", "risk3"],
    "negative_catalysts": ["catalyst1", "catalyst2"],
    "proposed_strategy": "description of defensive/short trade",
    "counter_to_bulls": ["counter1", "counter2"],
    "conviction_level": <1-10>,
    "argument_text": "full argument text"
}}
"""
        else:
            # Subsequent rounds - respond to bullish counterarguments
            bullish_args = [arg for arg in previous_arguments if arg.position == Sentiment.BULLISH]
            latest_bullish = bullish_args[-1] if bullish_args else None

            input_text = f"""
This is debate round {round_number} for {symbol}.

PREVIOUS BULLISH ARGUMENT:
{latest_bullish.argument if latest_bullish else 'No bullish argument yet'}

COUNTER these bullish points while strengthening your BEARISH case:

Respond with a rebuttal that:
1. Directly challenges the bullish assumptions
2. Provides additional evidence supporting your bearish view
3. Highlights risks that bulls are underestimating
4. Reinforces why this is an avoid or short opportunity

Provide your counter-argument in JSON format:
{{
    "counterpoints": ["counter1", "counter2", "counter3"],
    "additional_risks": ["risk1", "risk2"],
    "bullish_assumptions_flawed": ["flaw1", "flaw2"],
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
                    supporting_evidence = parsed.get("risks_and_concerns", [])
                    counterpoints = parsed.get("counter_to_bulls", [])
                else:
                    supporting_evidence = parsed.get("additional_risks", [])
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
                role=AgentRole.BEARISH_RESEARCHER,
                position=Sentiment.BEARISH,
                argument=argument_text,
                supporting_evidence=supporting_evidence,
                counterpoints=counterpoints,
            )

            logger.info(
                "Bearish argument complete",
                symbol=symbol,
                round=round_number,
                conviction=conviction,
            )

            return argument

        except Exception as e:
            logger.error("Bearish debate failed", symbol=symbol, round=round_number, error=str(e))

            return DebateArgument(
                round_number=round_number,
                role=AgentRole.BEARISH_RESEARCHER,
                position=Sentiment.BEARISH,
                argument=f"Error generating argument: {str(e)}",
                supporting_evidence=[],
                counterpoints=[],
            )
