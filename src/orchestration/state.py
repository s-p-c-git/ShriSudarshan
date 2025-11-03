"""
State definitions for LangGraph orchestration.

This module defines the state structure for the multi-agent workflow.
"""

from datetime import datetime
from typing import Optional, TypedDict

from ..data.schemas import (
    AgentReport,
    DebateArgument,
    ExecutionPlan,
    PortfolioDecision,
    RiskAssessment,
    StrategyProposal,
)


class TradingSystemState(TypedDict, total=False):
    """
    State structure for the trading system workflow.

    This state is passed between agents in the LangGraph workflow.
    """

    # Input parameters
    symbol: str
    start_date: Optional[str]
    end_date: Optional[str]

    # Analysis Phase
    analyst_reports: dict[str, AgentReport]
    analysis_complete: bool

    # Debate Phase
    debate_arguments: list[DebateArgument]
    debate_rounds: int
    debate_complete: bool

    # Strategy Phase
    strategy_proposal: Optional[StrategyProposal]
    strategy_complete: bool

    # Execution Planning Phase
    execution_plan: Optional[ExecutionPlan]
    execution_plan_complete: bool

    # Risk Assessment Phase
    risk_assessment: Optional[RiskAssessment]
    risk_approved: bool

    # Portfolio Decision Phase
    portfolio_decision: Optional[PortfolioDecision]
    final_approval: bool

    # Execution Phase
    orders_submitted: bool
    execution_complete: bool

    # Metadata
    workflow_start_time: datetime
    current_phase: str
    errors: list[str]


def create_initial_state(
    symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None
) -> TradingSystemState:
    """
    Create initial state for a trading workflow.

    Args:
        symbol: Stock symbol to analyze
        start_date: Optional start date for analysis
        end_date: Optional end date for analysis

    Returns:
        Initial TradingSystemState
    """
    return TradingSystemState(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        analyst_reports={},
        analysis_complete=False,
        debate_arguments=[],
        debate_rounds=0,
        debate_complete=False,
        strategy_proposal=None,
        strategy_complete=False,
        execution_plan=None,
        execution_plan_complete=False,
        risk_assessment=None,
        risk_approved=False,
        portfolio_decision=None,
        final_approval=False,
        orders_submitted=False,
        execution_complete=False,
        workflow_start_time=datetime.now(),
        current_phase="initialization",
        errors=[],
    )
