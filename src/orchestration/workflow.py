"""
LangGraph workflow orchestration for Project Shri Sudarshan.

This module defines the multi-agent workflow using LangGraph.
"""

from typing import Any

from langgraph.graph import END, StateGraph

from ..config import settings
from ..utils import get_logger
from .state import TradingSystemState, create_initial_state


logger = get_logger(__name__)


class TradingWorkflow:
    """
    LangGraph-based orchestration for the trading system.

    Manages the flow between analysis, debate, strategy, execution,
    and oversight phases.
    """

    def __init__(self):
        """Initialize the trading workflow."""
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine.

        Returns:
            Configured StateGraph
        """
        workflow = StateGraph(TradingSystemState)

        # Add nodes for each phase
        workflow.add_node("analysis", self._analysis_phase)
        workflow.add_node("debate", self._debate_phase)
        workflow.add_node("strategy", self._strategy_phase)
        workflow.add_node("execution_planning", self._execution_planning_phase)
        workflow.add_node("risk_assessment", self._risk_assessment_phase)
        workflow.add_node("portfolio_decision", self._portfolio_decision_phase)
        workflow.add_node("execution", self._execution_phase)
        workflow.add_node("learning", self._learning_phase)

        # Set entry point
        workflow.set_entry_point("analysis")

        # Add edges (phase transitions)
        workflow.add_edge("analysis", "debate")
        workflow.add_edge("debate", "strategy")
        workflow.add_edge("strategy", "execution_planning")
        workflow.add_edge("execution_planning", "risk_assessment")

        # Conditional edge: Risk approval required for portfolio decision
        workflow.add_conditional_edges(
            "risk_assessment",
            self._should_proceed_to_decision,
            {
                "proceed": "portfolio_decision",
                "reject": END,
            },
        )

        # Conditional edge: Portfolio approval required for execution
        workflow.add_conditional_edges(
            "portfolio_decision",
            self._should_execute,
            {
                "execute": "execution",
                "reject": END,
            },
        )

        workflow.add_edge("execution", "learning")
        workflow.add_edge("learning", END)

        return workflow.compile()

    async def _analysis_phase(self, state: TradingSystemState) -> TradingSystemState:
        """
        Market Intelligence Team analysis phase.

        All analysts run concurrently to produce reports.
        """
        logger.info("Starting analysis phase", symbol=state["symbol"])

        from ..agents.market_intelligence import (
            FinBERTSentimentAnalyst,
            FinGPTGenerativeAnalyst,
            FundamentalsAnalyst,
            MacroNewsAnalyst,
            SentimentAnalyst,
            TechnicalAnalyst,
        )
        from ..data.providers import MarketDataProvider, NewsProvider

        # Initialize analysts
        fundamentals_analyst = FundamentalsAnalyst()
        macro_news_analyst = MacroNewsAnalyst()
        sentiment_analyst = SentimentAnalyst()
        technical_analyst = TechnicalAnalyst()
        finbert_analyst = FinBERTSentimentAnalyst()
        fingpt_analyst = FinGPTGenerativeAnalyst()

        # Initialize data providers (shared across analysts)
        market_data_provider = MarketDataProvider()
        news_provider = NewsProvider()

        # Prepare context
        context = {
            "symbol": state["symbol"],
            "start_date": state.get("start_date"),
            "end_date": state.get("end_date"),
            "market_data_provider": market_data_provider,
            "news_provider": news_provider,
        }

        try:
            # Fetch news for specialized analysts (done once, outside conditional)
            news_items = news_provider.get_news(state["symbol"], limit=10)
            news_texts = [item["title"] + ". " + item.get("summary", "") for item in news_items]

            # Prepare contexts for specialized analysts
            finbert_context = {**context, "texts": news_texts}
            fingpt_context = {**context, "texts": news_texts, "analysis_type": "analyze_news"}

            # Run all analysts concurrently if enabled
            if settings.enable_concurrent_analysis:
                import asyncio

                logger.info("Running analysts concurrently")

                results = await asyncio.gather(
                    fundamentals_analyst.analyze(context),
                    macro_news_analyst.analyze(context),
                    sentiment_analyst.analyze(context),
                    technical_analyst.analyze(context),
                    finbert_analyst.analyze(finbert_context),
                    fingpt_analyst.analyze(fingpt_context),
                    return_exceptions=True,
                )

                # Unpack results
                fundamentals_report = results[0] if not isinstance(results[0], Exception) else None
                macro_news_report = results[1] if not isinstance(results[1], Exception) else None
                sentiment_report = results[2] if not isinstance(results[2], Exception) else None
                technical_report = results[3] if not isinstance(results[3], Exception) else None
                finbert_report = results[4] if not isinstance(results[4], Exception) else None
                fingpt_report = results[5] if not isinstance(results[5], Exception) else None

                # Log any errors
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        analyst_names = [
                            "Fundamentals",
                            "MacroNews",
                            "Sentiment",
                            "Technical",
                            "FinBERT",
                            "FinGPT",
                        ]
                        logger.warning(
                            "Analyst failed",
                            analyst=analyst_names[i],
                            error=str(result),
                        )
                        state["errors"].append(f"{analyst_names[i]} analysis failed: {str(result)}")
            else:
                # Run sequentially
                logger.info("Running analysts sequentially")

                fundamentals_report = await fundamentals_analyst.analyze(context)
                macro_news_report = await macro_news_analyst.analyze(context)
                sentiment_report = await sentiment_analyst.analyze(context)
                technical_report = await technical_analyst.analyze(context)

                finbert_report = await finbert_analyst.analyze(finbert_context)
                fingpt_report = await fingpt_analyst.analyze(fingpt_context)

            # Store reports
            state["analyst_reports"] = {
                "fundamentals": fundamentals_report,
                "macro_news": macro_news_report,
                "sentiment": sentiment_report,
                "technical": technical_report,
                "finbert": finbert_report,
                "fingpt": fingpt_report,
            }

            # Log summary
            logger.info(
                "Fundamentals analysis complete",
                result=(
                    fundamentals_report.investment_thesis.value if fundamentals_report else "failed"
                ),
            )
            logger.info(
                "Macro/News analysis complete",
                result=macro_news_report.market_sentiment.value if macro_news_report else "failed",
            )
            logger.info(
                "Sentiment analysis complete",
                result=sentiment_report.social_sentiment.value if sentiment_report else "failed",
            )
            logger.info(
                "Technical analysis complete",
                result=technical_report.trend_direction.value if technical_report else "failed",
            )
            if finbert_report:
                logger.info(
                    "FinBERT analysis complete",
                    sentiment=finbert_report.sentiment.value,
                    score=f"{finbert_report.sentiment_score:.2f}",
                )
            else:
                logger.warning("FinBERT analysis failed")

            if fingpt_report:
                logger.info(
                    "FinGPT analysis complete",
                    insights_count=len(fingpt_report.key_insights),
                )
            else:
                logger.warning("FinGPT analysis failed")

            state["analysis_complete"] = True
            state["current_phase"] = "analysis"

        except Exception as e:
            logger.error("Analysis phase failed", error=str(e))
            state["errors"].append(f"Analysis phase error: {str(e)}")
            state["analysis_complete"] = False

        return state

    async def _debate_phase(self, state: TradingSystemState) -> TradingSystemState:
        """
        Strategy & Research Team debate phase.

        Bullish and bearish researchers engage in multi-round debate.
        """
        print(f"[Debate Phase] Debating strategy for {state['symbol']}")

        from ..agents.strategy_research import BearishResearcher, BullishResearcher

        # Initialize researchers
        bullish_researcher = BullishResearcher()
        bearish_researcher = BearishResearcher()

        # Prepare context
        context = {
            "symbol": state["symbol"],
            "analyst_reports": state.get("analyst_reports", {}),
        }

        debate_arguments = []
        max_rounds = settings.max_debate_rounds

        try:
            print(f"  Starting {max_rounds}-round debate...")

            for round_num in range(1, max_rounds + 1):
                print(f"  Round {round_num}/{max_rounds}")

                # Bullish researcher argues first
                bullish_arg = await bullish_researcher.debate(
                    context,
                    round_number=round_num,
                    previous_arguments=debate_arguments,
                )
                debate_arguments.append(bullish_arg)
                print(f"    ✓ Bullish: {bullish_arg.argument[:100]}...")

                # Bearish researcher responds
                bearish_arg = await bearish_researcher.debate(
                    context,
                    round_number=round_num,
                    previous_arguments=debate_arguments,
                )
                debate_arguments.append(bearish_arg)
                print(f"    ✓ Bearish: {bearish_arg.argument[:100]}...")

            state["debate_arguments"] = debate_arguments
            state["debate_rounds"] = max_rounds
            state["debate_complete"] = True
            state["current_phase"] = "debate"

            print(f"  Debate concluded after {max_rounds} rounds")

        except Exception as e:
            print(f"  ✗ Debate phase failed: {e}")
            state["errors"].append(f"Debate phase error: {str(e)}")
            state["debate_arguments"] = debate_arguments  # Save what we have
            state["debate_complete"] = False

        return state

    async def _strategy_phase(self, state: TradingSystemState) -> TradingSystemState:
        """
        Derivatives Strategist formulates specific FnO strategy.
        """
        print(f"[Strategy Phase] Formulating strategy for {state['symbol']}")

        from ..agents.strategy_research import DerivativesStrategist
        from ..data.providers import MarketDataProvider

        # Initialize strategist
        derivatives_strategist = DerivativesStrategist()
        market_data_provider = MarketDataProvider()

        # Prepare context
        context = {
            "symbol": state["symbol"],
            "debate_arguments": state.get("debate_arguments", []),
            "analyst_reports": state.get("analyst_reports", {}),
            "market_data_provider": market_data_provider,
        }

        try:
            # Formulate strategy
            strategy_proposal = await derivatives_strategist.formulate_strategy(context)

            state["strategy_proposal"] = strategy_proposal
            state["strategy_complete"] = True
            state["current_phase"] = "strategy"

            print(
                f"  ✓ Strategy: {strategy_proposal.strategy_type.value} "
                f"({strategy_proposal.direction.value})"
            )
            print(
                f"  ✓ Expected Return: {strategy_proposal.expected_return:.1f}%, "
                f"Max Loss: {strategy_proposal.max_loss:.1f}%"
            )

        except Exception as e:
            print(f"  ✗ Strategy formulation failed: {e}")
            state["errors"].append(f"Strategy phase error: {str(e)}")
            state["strategy_complete"] = False
            state["current_phase"] = "strategy"

        return state

    async def _execution_planning_phase(self, state: TradingSystemState) -> TradingSystemState:
        """
        Execution Team creates detailed execution plan.
        """
        print(f"[Execution Planning Phase] Planning execution for {state['symbol']}")

        from ..agents.execution import EquityTrader, FnOTrader
        from ..data.providers import MarketDataProvider
        from ..data.schemas import StrategyType

        strategy_proposal = state.get("strategy_proposal")

        if not strategy_proposal:
            print("  ✗ No strategy proposal available")
            state["execution_plan_complete"] = False
            state["errors"].append("No strategy proposal for execution planning")
            return state

        # Select appropriate trader based on strategy type
        strategy_type = strategy_proposal.strategy_type

        # Options strategies use FnO trader, equity strategies use equity trader
        options_strategies = [
            StrategyType.COVERED_CALL,
            StrategyType.PROTECTIVE_PUT,
            StrategyType.BULL_CALL_SPREAD,
            StrategyType.BEAR_PUT_SPREAD,
            StrategyType.IRON_CONDOR,
            StrategyType.STRADDLE,
            StrategyType.STRANGLE,
            StrategyType.CALENDAR_SPREAD,
        ]

        if strategy_type in options_strategies:
            trader = FnOTrader()
            trader_type = "FnO"
        else:
            trader = EquityTrader()
            trader_type = "Equity"

        print(f"  Using {trader_type} Trader for {strategy_type.value}")

        # Prepare context
        market_data_provider = MarketDataProvider()
        context = {
            "symbol": state["symbol"],
            "strategy_proposal": strategy_proposal,
            "market_data_provider": market_data_provider,
            "portfolio_value": 100000.0,  # Default portfolio value
        }

        try:
            # Create execution plan
            execution_plan = await trader.create_execution_plan(context)

            state["execution_plan"] = execution_plan
            state["execution_plan_complete"] = True
            state["current_phase"] = "execution_planning"

            print(f"  ✓ Execution plan created: {len(execution_plan.orders)} order(s)")
            print(f"  ✓ Estimated cost: ${execution_plan.estimated_cost:.2f}")

        except Exception as e:
            print(f"  ✗ Execution planning failed: {e}")
            state["errors"].append(f"Execution planning error: {str(e)}")
            state["execution_plan_complete"] = False
            state["current_phase"] = "execution_planning"

        return state

    async def _risk_assessment_phase(self, state: TradingSystemState) -> TradingSystemState:
        """
        Risk Manager assesses the proposed trade.
        """
        print(f"[Risk Assessment Phase] Assessing risk for {state['symbol']}")

        from ..agents.oversight import RiskManager

        risk_manager = RiskManager()

        context = {
            "symbol": state["symbol"],
            "strategy_proposal": state.get("strategy_proposal"),
            "execution_plan": state.get("execution_plan"),
            "portfolio_state": {},  # Would come from portfolio tracking system
        }

        try:
            risk_assessment = await risk_manager.assess_risk(context)

            state["risk_assessment"] = risk_assessment
            state["risk_approved"] = risk_assessment.approved
            state["current_phase"] = "risk_assessment"

            approval_symbol = "✓" if risk_assessment.approved else "✗"
            print(f"  {approval_symbol} Risk Assessment: " f"{risk_assessment.recommendation}")
            if risk_assessment.risk_warnings:
                for warning in risk_assessment.risk_warnings[:3]:
                    print(f"    ⚠ {warning}")

        except Exception as e:
            print(f"  ✗ Risk assessment failed: {e}")
            state["errors"].append(f"Risk assessment error: {str(e)}")
            state["risk_approved"] = False
            state["current_phase"] = "risk_assessment"

        return state

    async def _portfolio_decision_phase(self, state: TradingSystemState) -> TradingSystemState:
        """
        Portfolio Manager makes final approval decision.
        """
        print(f"[Portfolio Decision Phase] Making decision for {state['symbol']}")

        from ..agents.oversight import PortfolioManager

        portfolio_manager = PortfolioManager()

        context = {
            "symbol": state["symbol"],
            "strategy_proposal": state.get("strategy_proposal"),
            "risk_assessment": state.get("risk_assessment"),
            "execution_plan": state.get("execution_plan"),
        }

        try:
            portfolio_decision = await portfolio_manager.make_decision(context)

            state["portfolio_decision"] = portfolio_decision
            state["final_approval"] = portfolio_decision.approved
            state["current_phase"] = "portfolio_decision"

            approval_symbol = "✓" if portfolio_decision.approved else "✗"
            decision_text = "APPROVED" if portfolio_decision.approved else "REJECTED"
            print(f"  {approval_symbol} Portfolio Manager Decision: {decision_text}")
            print(f"    {portfolio_decision.decision_rationale[:100]}...")

        except Exception as e:
            print(f"  ✗ Portfolio decision failed: {e}")
            state["errors"].append(f"Portfolio decision error: {str(e)}")
            state["final_approval"] = False
            state["current_phase"] = "portfolio_decision"

        return state

    async def _execution_phase(self, state: TradingSystemState) -> TradingSystemState:
        """
        Traders execute the approved strategy (PAPER TRADING MODE).
        """
        print(f"[Execution Phase] Executing strategy for {state['symbol']}")

        # In paper trading mode, we simulate execution
        execution_plan = state.get("execution_plan")

        if execution_plan and execution_plan.orders:
            print(f"  PAPER TRADING MODE - Simulating {len(execution_plan.orders)} order(s)")
            for i, order in enumerate(execution_plan.orders, 1):
                print(
                    f"    Order {i}: {order.side.value} {order.quantity} "
                    f"{order.symbol} @ {order.order_type.value}"
                )

            state["orders_submitted"] = True
            state["execution_complete"] = True
        else:
            print("  No orders to execute")
            state["orders_submitted"] = False
            state["execution_complete"] = True

        state["current_phase"] = "execution"

        return state

    async def _learning_phase(self, state: TradingSystemState) -> TradingSystemState:
        """
        Reflective Agent logs the trade for future learning.
        """
        print(f"[Learning Phase] Logging trade for {state['symbol']}")

        # In this phase, we would normally:
        # 1. Wait for trade to complete
        # 2. Calculate actual P&L
        # 3. Have reflective agent analyze outcome
        # For now, just log that we completed the workflow

        print("  Trade logged for future analysis")
        state["current_phase"] = "learning"

        return state

    def _should_proceed_to_decision(self, state: TradingSystemState) -> str:
        """Conditional edge: Check if risk assessment passed."""
        return "proceed" if state.get("risk_approved", False) else "reject"

    def _should_execute(self, state: TradingSystemState) -> str:
        """Conditional edge: Check if portfolio manager approved."""
        return "execute" if state.get("final_approval", False) else "reject"

    async def run(
        self, symbol: str, start_date: str = None, end_date: str = None
    ) -> dict[str, Any]:
        """
        Run the complete trading workflow for a symbol.

        Args:
            symbol: Stock symbol to analyze
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Final state dictionary
        """
        print(f"\n{'='*60}")
        print(f"Starting trading workflow for {symbol}")
        print(f"{'='*60}\n")

        # Create initial state
        initial_state = create_initial_state(symbol, start_date, end_date)

        # Run the workflow
        final_state = await self.graph.ainvoke(initial_state)

        print(f"\n{'='*60}")
        print(f"Workflow completed for {symbol}")
        print(f"Final phase: {final_state.get('current_phase', 'unknown')}")
        print(f"{'='*60}\n")

        return final_state
