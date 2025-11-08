"""Oversight & Learning Team - Risk Manager."""

import json
from typing import Any

from ...config import settings
from ...config.prompts import RISK_MANAGER_PROMPT
from ...data.schemas import (
    AgentReport,
    AgentRole,
    RiskAssessment,
    StrategyProposal,
)
from ...utils import get_logger
from ..base import CriticalAgent


logger = get_logger(__name__)


class RiskManager(CriticalAgent):
    """
    Risk Manager agent.

    Operates as independent oversight layer, assesses portfolio impact,
    and has veto authority over trades that violate risk parameters.
    """

    def __init__(self):
        super().__init__(
            role=AgentRole.RISK_MANAGER,
            system_prompt=RISK_MANAGER_PROMPT,
            temperature=0.3,  # Low temperature for conservative risk assessment
        )

    async def analyze(self, context: dict[str, Any]) -> AgentReport:
        """
        Main entry point - delegates to assess_risk.

        Args:
            context: Contains strategy_proposal, execution_plan, portfolio_state

        Returns:
            AgentReport with risk assessment details
        """
        assessment = await self.assess_risk(context)
        symbol = context.get("symbol", "UNKNOWN")

        return AgentReport(
            agent_role=self.role,
            symbol=symbol,
            summary=f"Risk assessment: {'APPROVED' if assessment.approved else 'REJECTED'}",
            confidence=0.9,
            metadata={"risk_assessment": assessment.model_dump()},
        )

    async def assess_risk(self, context: dict[str, Any]) -> RiskAssessment:
        """
        Assess risk of proposed trade.

        Args:
            context: Contains strategy_proposal, execution_plan, portfolio_state

        Returns:
            RiskAssessment with approval/rejection
        """
        symbol = context.get("symbol", "UNKNOWN")
        strategy_proposal: StrategyProposal = context.get("strategy_proposal")
        portfolio_state = context.get("portfolio_state", {})

        logger.info("Assessing risk", symbol=symbol)

        try:
            # Get portfolio metrics
            portfolio_value = portfolio_state.get("total_value", 100000.0)
            sector_exposures = portfolio_state.get("sector_exposures", {})

            # Calculate position size check
            position_value = portfolio_value * strategy_proposal.position_size_pct
            max_position_value = portfolio_value * settings.max_position_size
            position_size_ok = position_value <= max_position_value

            # Calculate VaR impact (simplified)
            # In production, would use proper VaR calculations
            estimated_var = abs(strategy_proposal.max_loss) / 100 * position_value
            current_var = portfolio_state.get("var", 0.0)
            projected_var = current_var + estimated_var
            var_limit = portfolio_value * settings.max_portfolio_risk
            var_ok = projected_var <= var_limit

            # Check sector concentration (simplified)
            # Would need actual sector data in production
            sector = "Unknown"
            current_sector_exposure = sector_exposures.get(sector, 0.0)
            new_sector_exposure = current_sector_exposure + position_value
            sector_concentration = new_sector_exposure / portfolio_value
            sector_ok = sector_concentration <= settings.max_sector_concentration

            # Compile risk warnings
            risk_warnings = []
            if not position_size_ok:
                risk_warnings.append(
                    f"Position size ${position_value:.0f} exceeds limit ${max_position_value:.0f}"
                )
            if not var_ok:
                risk_warnings.append(
                    f"Projected VaR ${projected_var:.0f} exceeds limit ${var_limit:.0f}"
                )
            if not sector_ok:
                risk_warnings.append(
                    f"Sector concentration {sector_concentration * 100:.1f}% exceeds {settings.max_sector_concentration * 100:.0f}%"
                )

            # Additional qualitative risk assessment
            if strategy_proposal.confidence_score < 0.5:
                risk_warnings.append("Low strategy confidence score")

            if abs(strategy_proposal.max_loss) > 10:
                risk_warnings.append(
                    f"High maximum loss potential: {strategy_proposal.max_loss:.1f}%"
                )

            # Construct input for LLM
            input_text = f"""
Assess the risk of the proposed trade for {symbol}.

STRATEGY:
- Type: {strategy_proposal.strategy_type.value}
- Direction: {strategy_proposal.direction.value}
- Position Size: {strategy_proposal.position_size_pct * 100:.1f}% (${position_value:.0f})
- Expected Return: {strategy_proposal.expected_return:.1f}%
- Max Loss: {strategy_proposal.max_loss:.1f}%
- Confidence: {strategy_proposal.confidence_score:.2f}

RISK PARAMETERS:
- Max Position Size: {settings.max_position_size * 100:.0f}% (${max_position_value:.0f})
- Max Portfolio Risk (VaR): {settings.max_portfolio_risk * 100:.0f}% (${var_limit:.0f})
- Max Sector Concentration: {settings.max_sector_concentration * 100:.0f}%

CHECKS:
- Position Size Check: {"PASS" if position_size_ok else "FAIL"}
- VaR Check: {"PASS" if var_ok else "FAIL"}
- Sector Check: {"PASS" if sector_ok else "FAIL"}

WARNINGS:
{chr(10).join([f"- {w}" for w in risk_warnings]) if risk_warnings else "- None"}

As Risk Manager, provide your assessment in JSON format:
{{
    "approved": true or false,
    "risk_score": <0.0 to 1.0>,
    "recommendation": "approve", "modify", or "reject",
    "rationale": "brief explanation of decision",
    "additional_warnings": ["warning1", "warning2"]
}}

Note: You have VETO AUTHORITY. If risk parameters are violated or the risk is unacceptable, you MUST reject the trade.
"""

            # Generate assessment
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

                llm_approved = parsed.get("approved", True)
                risk_score = float(parsed.get("risk_score", 0.5))
                recommendation = parsed.get("recommendation", "approve")
                rationale = parsed.get("rationale", response[:200])
                additional_warnings = parsed.get("additional_warnings", [])

                risk_warnings.extend(additional_warnings)

            except (json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
                logger.warning(
                    "Failed to parse LLM response, using rule-based decision",
                    error=str(e),
                )
                llm_approved = True
                risk_score = 0.5
                recommendation = "approve"
                rationale = "Rule-based assessment"

            # Final decision: Must pass hard limits AND LLM approval
            hard_limits_passed = position_size_ok and var_ok and sector_ok
            final_approved = hard_limits_passed and llm_approved

            if not hard_limits_passed:
                recommendation = "reject"
                rationale = "Hard risk limits violated"

            # Calculate portfolio impact
            portfolio_impact = {
                "position_value": position_value,
                "position_pct": strategy_proposal.position_size_pct * 100,
                "var_increase": estimated_var,
                "projected_var": projected_var,
            }

            assessment = RiskAssessment(
                symbol=symbol,
                approved=final_approved,
                portfolio_impact=portfolio_impact,
                var_impact=estimated_var,
                sector_concentration=sector_concentration,
                position_size_check=position_size_ok,
                risk_warnings=risk_warnings,
                risk_score=risk_score,
                recommendation=f"{recommendation}: {rationale}",
            )

            logger.info(
                "Risk assessment complete",
                symbol=symbol,
                approved=final_approved,
                risk_score=risk_score,
            )

            return assessment

        except Exception as e:
            logger.error("Risk assessment failed", symbol=symbol, error=str(e))

            # Conservative default: reject on error
            return RiskAssessment(
                symbol=symbol,
                approved=False,
                portfolio_impact={},
                var_impact=0.0,
                sector_concentration=0.0,
                position_size_check=False,
                risk_warnings=[f"Risk assessment error: {str(e)}"],
                risk_score=1.0,
                recommendation="reject: Assessment failed",
            )
