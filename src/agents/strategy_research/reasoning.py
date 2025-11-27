"""Strategy & Research Team - DeepSeek R1 Reasoning Agent.

This module implements the "Cognitive Core" of the Deep Reasoner v2.0 architecture.
It uses DeepSeek-R1 for Chain-of-Thought reasoning to validate complex trading strategies.

SECURITY WARNING:
    Do NOT install packages named 'deepseek' or 'deepseeek' from PyPI.
    These are confirmed malware vectors. Use the standard OpenAI SDK
    with base_url="https://api.deepseek.com".
"""

import json
from typing import Any, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ...config import settings
from ...config.prompts import DEEPSEEK_REASONING_AGENT_PROMPT
from ...data.schemas import (
    AgentRole,
    DeepSeekReasoningReport,
    StrategyProposal,
)
from ...utils import get_logger
from ..base import CriticalAgent


logger = get_logger(__name__)


class DeepSeekReasoningAgent(CriticalAgent):
    """
    DeepSeek R1 Reasoning Agent (Cognitive Core).

    Uses DeepSeek-R1 via OpenAI SDK to perform Chain-of-Thought reasoning
    for mathematical validation of complex trading strategies.

    Key Features:
        - CoT reasoning traces for auditability
        - Self-correction loop for strategy refinement
        - Mathematical validation of option spreads and hedging
        - Reasoning content logged but stripped from multi-turn context

    Latency Profile:
        - Inference: ~10-60s (Slow Loop)
        - Use for strategic decisions, not real-time execution
    """

    def __init__(self):
        """Initialize DeepSeek Reasoning Agent."""
        super().__init__(
            role=AgentRole.DEEPSEEK_REASONING_AGENT,
            system_prompt=DEEPSEEK_REASONING_AGENT_PROMPT,
            temperature=0.3,  # Lower temperature for more deterministic reasoning
        )

        # Initialize DeepSeek R1 LLM using OpenAI SDK
        self._reasoning_llm: Optional[ChatOpenAI] = None

    def _get_reasoning_llm(self) -> ChatOpenAI:
        """
        Get or create the DeepSeek R1 reasoning LLM.

        Uses OpenAI SDK with custom base_url for DeepSeek API.

        Returns:
            ChatOpenAI configured for DeepSeek R1
        """
        if self._reasoning_llm is None:
            api_key = settings.deepseek_api_key or settings.openai_api_key
            self._reasoning_llm = ChatOpenAI(
                model=settings.deepseek_reasoner_model,
                temperature=0.3,
                openai_api_key=api_key,
                openai_api_base=settings.deepseek_base_url,
            )
        return self._reasoning_llm

    async def _generate_reasoning_response(self, input_text: str) -> tuple[str, str]:
        """
        Generate response using DeepSeek R1 with reasoning extraction.

        Args:
            input_text: The input prompt

        Returns:
            Tuple of (response_content, reasoning_content)
            reasoning_content is logged for auditability but stripped from context
        """
        try:
            llm = self._get_reasoning_llm()
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=input_text),
            ]

            response = await llm.ainvoke(messages)
            content = response.content

            # Extract reasoning content if present (DeepSeek R1 format)
            # The reasoning_content is typically in a special format
            reasoning_content = ""
            if hasattr(response, "additional_kwargs"):
                reasoning_content = response.additional_kwargs.get("reasoning_content", "")

            # Log reasoning for auditability
            if reasoning_content:
                logger.info(
                    "DeepSeek R1 reasoning trace captured",
                    reasoning_length=len(reasoning_content),
                )

            return content, reasoning_content

        except Exception as e:
            logger.warning(
                "DeepSeek R1 unavailable, falling back to standard LLM",
                error=str(e),
            )
            # Fallback to standard LLM
            response = await self._generate_response(input_text)
            return response, ""

    async def analyze(self, context: dict[str, Any]) -> DeepSeekReasoningReport:
        """
        Analyze and validate a strategy proposal using CoT reasoning.

        Args:
            context: Contains strategy_proposal, analyst_reports, etc.

        Returns:
            DeepSeekReasoningReport with validation results
        """
        symbol = context.get("symbol", "UNKNOWN")
        strategy_proposal: Optional[StrategyProposal] = context.get("strategy_proposal")

        logger.info("Starting DeepSeek R1 strategy validation", symbol=symbol)

        if not strategy_proposal:
            return DeepSeekReasoningReport(
                symbol=symbol,
                summary="No strategy proposal to validate",
                confidence=0.0,
                strategy_validated=False,
                approval_status="rejected",
            )

        try:
            # Prepare validation prompt
            validation_prompt = self._build_validation_prompt(context)

            # Generate reasoning response
            response, reasoning_trace = await self._generate_reasoning_response(
                validation_prompt
            )

            # Parse the response
            report = self._parse_validation_response(
                symbol=symbol,
                response=response,
                reasoning_trace=reasoning_trace,
            )

            # Self-correction loop
            if report.confidence < 0.7:
                report = await self._self_correct(context, report)

            logger.info(
                "Strategy validation complete",
                symbol=symbol,
                validated=report.strategy_validated,
                confidence=report.confidence,
            )

            return report

        except Exception as e:
            logger.error("Strategy validation failed", symbol=symbol, error=str(e))
            return DeepSeekReasoningReport(
                symbol=symbol,
                summary=f"Validation failed: {str(e)}",
                confidence=0.1,
                strategy_validated=False,
                approval_status="rejected",
            )

    def _build_validation_prompt(self, context: dict[str, Any]) -> str:
        """Build the validation prompt for DeepSeek R1."""
        strategy = context.get("strategy_proposal")
        analyst_reports = context.get("analyst_reports", {})

        # Extract key data from reports
        technical = analyst_reports.get("technical")
        fundamentals = analyst_reports.get("fundamentals")

        # Handle direction as either enum or string
        direction_value = (
            strategy.direction.value
            if hasattr(strategy.direction, "value")
            else str(strategy.direction)
        )

        # Handle analyst report values
        tech_trend = "N/A"
        if technical:
            tech_trend = (
                technical.trend_direction.value
                if hasattr(technical.trend_direction, "value")
                else str(technical.trend_direction)
            )

        fund_thesis = "N/A"
        if fundamentals:
            fund_thesis = (
                fundamentals.investment_thesis.value
                if hasattr(fundamentals.investment_thesis, "value")
                else str(fundamentals.investment_thesis)
            )

        prompt = f"""
Validate the following trading strategy using mathematical reasoning.

STRATEGY PROPOSAL:
- Symbol: {strategy.symbol}
- Strategy Type: {strategy.strategy_type}
- Direction: {direction_value}
- Expected Return: {strategy.expected_return}%
- Max Loss: {strategy.max_loss}%
- Position Size: {strategy.position_size_pct * 100}%
- Time Horizon: {strategy.time_horizon_days} days
- Rationale: {strategy.rationale}

ENTRY CONDITIONS:
{chr(10).join([f"- {c}" for c in strategy.entry_conditions])}

EXIT CONDITIONS:
{chr(10).join([f"- {c}" for c in strategy.exit_conditions])}

SUPPORTING ANALYSIS:
- Technical Trend: {tech_trend}
- Technical Confidence: {technical.confidence if technical else "N/A"}
- Fundamentals Thesis: {fund_thesis}

VALIDATION TASKS:
1. Mathematically validate the expected return vs max loss ratio
2. Assess if position sizing is appropriate for the risk level
3. Evaluate entry/exit conditions for logical consistency
4. Calculate estimated risk metrics (Greeks if options)
5. Identify any hedging requirements
6. Self-critique: What could be wrong with this analysis?

Provide your validation in JSON format:
{{
    "strategy_validated": true/false,
    "approval_status": "approved" or "rejected" or "needs_modification",
    "mathematical_analysis": "detailed analysis",
    "risk_metrics": {{
        "risk_reward_ratio": <number>,
        "expected_sharpe": <number>,
        "max_drawdown_estimate": <percentage>
    }},
    "hedging_recommendation": "recommendation if needed",
    "self_correction_notes": ["note1", "note2"],
    "confidence_score": <0.0-1.0>,
    "summary": "brief summary"
}}
"""
        return prompt

    def _parse_validation_response(
        self,
        symbol: str,
        response: str,
        reasoning_trace: str,
    ) -> DeepSeekReasoningReport:
        """Parse the validation response into a report."""
        try:
            # Extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            parsed = json.loads(json_str)

            return DeepSeekReasoningReport(
                symbol=symbol,
                summary=parsed.get("summary", "Validation complete"),
                confidence=float(parsed.get("confidence_score", 0.5)),
                reasoning_trace=reasoning_trace,
                strategy_validated=parsed.get("strategy_validated", False),
                validation_details=parsed,
                mathematical_analysis=parsed.get("mathematical_analysis", ""),
                hedging_recommendation=parsed.get("hedging_recommendation"),
                risk_metrics=parsed.get("risk_metrics", {}),
                self_correction_notes=parsed.get("self_correction_notes", []),
                approval_status=parsed.get("approval_status", "pending"),
            )

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Failed to parse validation response", error=str(e))
            return DeepSeekReasoningReport(
                symbol=symbol,
                summary=response[:500],
                confidence=0.3,
                reasoning_trace=reasoning_trace,
                strategy_validated=False,
                approval_status="needs_modification",
            )

    async def _self_correct(
        self,
        context: dict[str, Any],
        initial_report: DeepSeekReasoningReport,
    ) -> DeepSeekReasoningReport:
        """
        Perform self-correction on low-confidence validations.

        Args:
            context: Original context
            initial_report: Initial validation report

        Returns:
            Refined DeepSeekReasoningReport
        """
        logger.info("Performing self-correction loop", symbol=initial_report.symbol)

        correction_prompt = f"""
Your initial validation had low confidence ({initial_report.confidence}).

INITIAL ASSESSMENT:
{initial_report.summary}

SELF-CORRECTION NOTES:
{chr(10).join(initial_report.self_correction_notes)}

Please re-evaluate your analysis:
1. What assumptions may have been incorrect?
2. Are there alternative interpretations?
3. What additional information would help?
4. Provide a refined assessment with updated confidence.

Respond in JSON format with the same structure as before.
"""

        response, reasoning = await self._generate_reasoning_response(correction_prompt)

        # Merge reasoning traces
        combined_reasoning = f"""
=== INITIAL REASONING ===
{initial_report.reasoning_trace}

=== SELF-CORRECTION REASONING ===
{reasoning}
"""

        refined_report = self._parse_validation_response(
            symbol=initial_report.symbol,
            response=response,
            reasoning_trace=combined_reasoning,
        )

        # Add self-correction note
        refined_report.self_correction_notes.append(
            f"Self-correction applied. Initial confidence: {initial_report.confidence}"
        )

        return refined_report
