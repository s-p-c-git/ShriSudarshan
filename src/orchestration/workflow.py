"""
LangGraph workflow orchestration for Project Shri Sudarshan.

This module defines the multi-agent workflow using LangGraph.
"""

from typing import Any, Dict

from langgraph.graph import StateGraph, END

from .state import TradingSystemState, create_initial_state
from ..config import settings


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
            }
        )
        
        # Conditional edge: Portfolio approval required for execution
        workflow.add_conditional_edges(
            "portfolio_decision",
            self._should_execute,
            {
                "execute": "execution",
                "reject": END,
            }
        )
        
        workflow.add_edge("execution", "learning")
        workflow.add_edge("learning", END)
        
        return workflow.compile()
    
    async def _analysis_phase(self, state: TradingSystemState) -> TradingSystemState:
        """
        Market Intelligence Team analysis phase.
        
        All analysts run concurrently to produce reports.
        """
        print(f"[Analysis Phase] Analyzing {state['symbol']}")
        
        from ..agents.market_intelligence import (
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
            # Run all analysts concurrently if enabled
            if settings.enable_concurrent_analysis:
                import asyncio
                
                print("  Running analysts concurrently...")
                results = await asyncio.gather(
                    fundamentals_analyst.analyze(context),
                    macro_news_analyst.analyze(context),
                    sentiment_analyst.analyze(context),
                    technical_analyst.analyze(context),
                    return_exceptions=True,
                )
                
                # Unpack results
                fundamentals_report = results[0] if not isinstance(results[0], Exception) else None
                macro_news_report = results[1] if not isinstance(results[1], Exception) else None
                sentiment_report = results[2] if not isinstance(results[2], Exception) else None
                technical_report = results[3] if not isinstance(results[3], Exception) else None
                
                # Log any errors
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        analyst_names = ["Fundamentals", "MacroNews", "Sentiment", "Technical"]
                        print(f"  ⚠ {analyst_names[i]} Analyst failed: {result}")
                        state["errors"].append(f"{analyst_names[i]} analysis failed: {str(result)}")
            else:
                # Run sequentially
                print("  Running analysts sequentially...")
                fundamentals_report = await fundamentals_analyst.analyze(context)
                macro_news_report = await macro_news_analyst.analyze(context)
                sentiment_report = await sentiment_analyst.analyze(context)
                technical_report = await technical_analyst.analyze(context)
            
            # Store reports
            state["analyst_reports"] = {
                "fundamentals": fundamentals_report,
                "macro_news": macro_news_report,
                "sentiment": sentiment_report,
                "technical": technical_report,
            }
            
            # Print summary
            print(f"  ✓ Fundamentals: {fundamentals_report.investment_thesis.value if fundamentals_report else 'failed'}")
            print(f"  ✓ Macro/News: {macro_news_report.market_sentiment.value if macro_news_report else 'failed'}")
            print(f"  ✓ Sentiment: {sentiment_report.social_sentiment.value if sentiment_report else 'failed'}")
            print(f"  ✓ Technical: {technical_report.trend_direction.value if technical_report else 'failed'}")
            
            state["analysis_complete"] = True
            state["current_phase"] = "analysis"
            
        except Exception as e:
            print(f"  ✗ Analysis phase failed: {e}")
            state["errors"].append(f"Analysis phase error: {str(e)}")
            state["analysis_complete"] = False
        
        return state
    
    async def _debate_phase(self, state: TradingSystemState) -> TradingSystemState:
        """
        Strategy & Research Team debate phase.
        
        Bullish and bearish researchers debate the strategy.
        """
        print(f"[Debate Phase] Debating strategy for {state['symbol']}")
        
        # TODO: Implement multi-round debate mechanism
        state["debate_complete"] = True
        state["current_phase"] = "debate"
        state["debate_rounds"] = 1
        
        return state
    
    async def _strategy_phase(self, state: TradingSystemState) -> TradingSystemState:
        """
        Derivatives Strategist formulates specific FnO strategy.
        """
        print(f"[Strategy Phase] Formulating strategy for {state['symbol']}")
        
        # TODO: Implement strategy formulation
        state["strategy_complete"] = True
        state["current_phase"] = "strategy"
        
        return state
    
    async def _execution_planning_phase(self, state: TradingSystemState) -> TradingSystemState:
        """
        Execution Team creates detailed execution plan.
        """
        print(f"[Execution Planning Phase] Planning execution for {state['symbol']}")
        
        # TODO: Implement execution planning
        state["execution_plan_complete"] = True
        state["current_phase"] = "execution_planning"
        
        return state
    
    async def _risk_assessment_phase(self, state: TradingSystemState) -> TradingSystemState:
        """
        Risk Manager assesses the proposed trade.
        """
        print(f"[Risk Assessment Phase] Assessing risk for {state['symbol']}")
        
        # TODO: Implement risk assessment
        # For now, approve by default
        state["risk_approved"] = True
        state["current_phase"] = "risk_assessment"
        
        return state
    
    async def _portfolio_decision_phase(self, state: TradingSystemState) -> TradingSystemState:
        """
        Portfolio Manager makes final approval decision.
        """
        print(f"[Portfolio Decision Phase] Making decision for {state['symbol']}")
        
        # TODO: Implement portfolio decision logic
        # For now, approve by default
        state["final_approval"] = True
        state["current_phase"] = "portfolio_decision"
        
        return state
    
    async def _execution_phase(self, state: TradingSystemState) -> TradingSystemState:
        """
        Traders execute the approved strategy.
        """
        print(f"[Execution Phase] Executing strategy for {state['symbol']}")
        
        # TODO: Implement order execution
        state["execution_complete"] = True
        state["current_phase"] = "execution"
        
        return state
    
    async def _learning_phase(self, state: TradingSystemState) -> TradingSystemState:
        """
        Reflective Agent logs the trade for future learning.
        """
        print(f"[Learning Phase] Logging trade for {state['symbol']}")
        
        # TODO: Implement learning loop
        state["current_phase"] = "learning"
        
        return state
    
    def _should_proceed_to_decision(self, state: TradingSystemState) -> str:
        """Conditional edge: Check if risk assessment passed."""
        return "proceed" if state.get("risk_approved", False) else "reject"
    
    def _should_execute(self, state: TradingSystemState) -> str:
        """Conditional edge: Check if portfolio manager approved."""
        return "execute" if state.get("final_approval", False) else "reject"
    
    async def run(self, symbol: str, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
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
