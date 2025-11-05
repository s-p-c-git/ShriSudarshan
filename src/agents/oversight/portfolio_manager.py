"""Oversight & Learning Team - Portfolio Manager."""

import json
from typing import Any

from ...config.prompts import PORTFOLIO_MANAGER_PROMPT
from ...data.schemas import (
    AgentRole,
    PortfolioDecision,
    RiskAssessment,
    StrategyProposal,
)
from ...utils import get_logger
from ..base import CriticalAgent


logger = get_logger(__name__)


class PortfolioManager(CriticalAgent):
    """
    Portfolio Manager agent.

    Makes final approval/rejection decisions on trade proposals.
    Central decision-making authority for the system.
    """

    def __init__(self):
        super().__init__(
            role=AgentRole.PORTFOLIO_MANAGER,
            system_prompt=PORTFOLIO_MANAGER_PROMPT,
            temperature=0.4,
        )

    async def make_decision(self, context: dict[str, Any]) -> PortfolioDecision:
        """
        Make final decision on trade proposal.

        Args:
            context: Contains all analysis, debate, strategy, risk assessment

        Returns:
            PortfolioDecision with final approval
        """
        symbol = context.get("symbol", "UNKNOWN")
        strategy_proposal: StrategyProposal = context.get("strategy_proposal")
        risk_assessment: RiskAssessment = context.get("risk_assessment")

        logger.info("Making portfolio decision", symbol=symbol)

        try:
            # Summarize key information
            debate_summary = strategy_proposal.debate_summary if strategy_proposal else "No debate"
            risk_approved = risk_assessment.approved if risk_assessment else False
            risk_score = risk_assessment.risk_score if risk_assessment else 1.0

            # Construct input for LLM
            input_text = f"""
Make the FINAL decision on whether to approve the trade for {symbol}.

STRATEGY PROPOSAL:
- Type: {strategy_proposal.strategy_type.value if strategy_proposal else "N/A"}
- Direction: {strategy_proposal.direction.value if strategy_proposal else "N/A"}
- Expected Return: {strategy_proposal.expected_return if strategy_proposal else 0}%
- Max Loss: {strategy_proposal.max_loss if strategy_proposal else 0}%
- Confidence: {strategy_proposal.confidence_score if strategy_proposal else 0}

RISK ASSESSMENT:
- Risk Manager Approval: {"APPROVED" if risk_approved else "REJECTED"}
- Risk Score: {risk_score:.2f} (0=low risk, 1=high risk)
- Warnings: {len(risk_assessment.risk_warnings) if risk_assessment else 0}

DEBATE SUMMARY:
{debate_summary[:500]}

As Portfolio Manager, make your final decision in JSON format:
{{
    "approved": true or false,
    "rationale": "explanation of your decision",
    "monitoring_requirements": ["requirement1", "requirement2"],
    "exit_triggers": ["trigger1", "trigger2"]
}}

Consider:
- Strategic fit with portfolio objectives
- Risk/reward profile
- Market conditions
- Confidence levels
"""

            # Generate decision
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

                approved = parsed.get("approved", False)
                rationale = parsed.get("rationale", response[:300])
                monitoring = parsed.get("monitoring_requirements", [])
                exit_triggers = parsed.get("exit_triggers", [])

            except (json.JSONDecodeError, KeyError, IndexError) as e:
                logger.warning("Failed to parse response, using conservative default", error=str(e))
                approved = False
                rationale = "Could not parse decision - rejecting for safety"
                monitoring = []
                exit_triggers = []

            # Override if risk manager rejected
            if not risk_approved:
                approved = False
                rationale = f"Risk Manager rejected trade. {rationale}"

            decision = PortfolioDecision(
                symbol=symbol,
                approved=approved,
                decision_rationale=rationale,
                adjusted_position_size=None,
                monitoring_requirements=monitoring,
                exit_triggers=exit_triggers,
                notes="",
            )

            logger.info(
                "Portfolio decision made",
                symbol=symbol,
                approved=approved,
            )

            return decision

        except Exception as e:
            logger.error("Portfolio decision failed", symbol=symbol, error=str(e))

            # Conservative default: reject on error
            return PortfolioDecision(
                symbol=symbol,
                approved=False,
                decision_rationale=f"Decision error: {str(e)}",
                adjusted_position_size=None,
                monitoring_requirements=[],
                exit_triggers=[],
                notes="Error occurred",
            )
