"""
Mock agent implementations for testing without LLM API calls.

This module provides mock versions of all agents that return deterministic
data without making actual LLM API calls, enabling fast and reliable testing.
"""

from typing import Any, Optional
from unittest.mock import AsyncMock

from src.agents.base import BaseAgent, CriticalAgent
from src.data.schemas import (
    AgentRole,
    AgentReport,
    DebateArgument,
    ExecutionPlan,
    FundamentalsReport,
    MacroNewsReport,
    Order,
    OrderSide,
    OrderType,
    PortfolioDecision,
    RiskAssessment,
    Sentiment,
    SentimentReport,
    StrategyProposal,
    StrategyType,
    TechnicalReport,
    TradeDirection,
    TrendDirection,
)


class MockBaseAgent(BaseAgent):
    """
    Mock base agent that doesn't call LLM APIs.
    
    Can be used to test agent workflow without API dependencies.
    """

    def __init__(
        self,
        role: AgentRole,
        system_prompt: str,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        provider: Optional[str] = None,
    ):
        """Initialize mock agent with AsyncMock for LLM."""
        # Initialize parent but we'll replace the LLM with a mock
        super().__init__(
            role=role,
            system_prompt=system_prompt,
            model_name=model_name,
            temperature=temperature,
            provider=provider,
        )
        
        # Replace LLM with AsyncMock
        mock_response = AsyncMock()
        mock_response.content = "Mock LLM response"
        self.llm = AsyncMock()
        self.llm.ainvoke.return_value = mock_response

    async def analyze(self, context: dict[str, Any]) -> AgentReport:
        """Mock analyze method - override in subclasses."""
        return AgentReport(
            agent_role=self.role,
            symbol=context.get("symbol", "TEST"),
            summary="Mock analysis",
            confidence=0.8,
        )


class MockCriticalAgent(CriticalAgent):
    """
    Mock critical agent that doesn't call LLM APIs.
    
    Can be used to test critical agent workflow without API dependencies.
    """

    def __init__(
        self,
        role: AgentRole,
        system_prompt: str,
        temperature: float = 0.7,
        provider: Optional[str] = None,
    ):
        """Initialize mock critical agent with AsyncMock for LLM."""
        # Initialize parent but we'll replace the LLM with a mock
        super().__init__(
            role=role,
            system_prompt=system_prompt,
            temperature=temperature,
            provider=provider,
        )
        
        # Replace LLM with AsyncMock
        mock_response = AsyncMock()
        mock_response.content = "Mock LLM response"
        self.llm = AsyncMock()
        self.llm.ainvoke.return_value = mock_response


# =============================================================================
# Mock Market Intelligence Agents
# =============================================================================


class MockFundamentalsAnalyst(MockBaseAgent):
    """Mock Fundamentals Analyst that returns deterministic data."""

    def __init__(self):
        super().__init__(
            role=AgentRole.FUNDAMENTALS_ANALYST,
            system_prompt="Mock fundamentals analyst",
            temperature=0.5,
        )

    async def analyze(self, context: dict[str, Any]) -> FundamentalsReport:
        """Return mock fundamentals report."""
        symbol = context.get("symbol", "TEST")
        
        return FundamentalsReport(
            agent_role=AgentRole.FUNDAMENTALS_ANALYST,
            symbol=symbol,
            summary="Strong fundamentals with solid profitability metrics",
            confidence=0.85,
            revenue=394328000000,
            net_income=99803000000,
            pe_ratio=28.5,
            pb_ratio=45.2,
            ps_ratio=7.6,
            roe=1.47,
            roa=0.28,
            debt_to_equity=1.97,
            current_ratio=0.98,
            intrinsic_value=210.00,
            current_price=195.50,
            investment_thesis=Sentiment.BULLISH,
        )


class MockTechnicalAnalyst(MockBaseAgent):
    """Mock Technical Analyst that returns deterministic data."""

    def __init__(self):
        super().__init__(
            role=AgentRole.TECHNICAL_ANALYST,
            system_prompt="Mock technical analyst",
            temperature=0.5,
        )

    async def analyze(self, context: dict[str, Any]) -> TechnicalReport:
        """Return mock technical report."""
        symbol = context.get("symbol", "TEST")
        
        return TechnicalReport(
            agent_role=AgentRole.TECHNICAL_ANALYST,
            symbol=symbol,
            summary="Strong uptrend with bullish indicators",
            confidence=0.8,
            trend_direction=TrendDirection.UPTREND,
            support_levels=[190.0, 185.0, 180.0],
            resistance_levels=[200.0, 205.0, 210.0],
            chart_patterns=["ascending triangle", "golden cross"],
            indicators={"rsi": 65.5, "macd": "bullish", "sma_20": 195.0},
            volatility=0.25,
        )


class MockSentimentAnalyst(MockBaseAgent):
    """Mock Sentiment Analyst that returns deterministic data."""

    def __init__(self):
        super().__init__(
            role=AgentRole.SENTIMENT_ANALYST,
            system_prompt="Mock sentiment analyst",
            temperature=0.5,
        )

    async def analyze(self, context: dict[str, Any]) -> SentimentReport:
        """Return mock sentiment report."""
        symbol = context.get("symbol", "TEST")
        
        return SentimentReport(
            agent_role=AgentRole.SENTIMENT_ANALYST,
            symbol=symbol,
            summary="Positive social sentiment with increasing retail interest",
            confidence=0.75,
            social_sentiment=Sentiment.BULLISH,
            sentiment_score=0.65,
            volume_trend="increasing",
            retail_interest="high",
            institutional_activity="moderate",
        )


class MockMacroNewsAnalyst(MockBaseAgent):
    """Mock Macro/News Analyst that returns deterministic data."""

    def __init__(self):
        super().__init__(
            role=AgentRole.MACRO_NEWS_ANALYST,
            system_prompt="Mock macro news analyst",
            temperature=0.5,
        )

    async def analyze(self, context: dict[str, Any]) -> MacroNewsReport:
        """Return mock macro news report."""
        symbol = context.get("symbol", "TEST")
        
        return MacroNewsReport(
            agent_role=AgentRole.MACRO_NEWS_ANALYST,
            symbol=symbol,
            summary="Positive market conditions with supportive monetary policy",
            confidence=0.7,
            market_sentiment=Sentiment.BULLISH,
            key_events=["Fed maintains rates", "Strong GDP growth"],
            geopolitical_risks=["Trade tensions"],
            economic_indicators={"gdp_growth": 2.5, "inflation": 2.1},
            news_sentiment=0.6,
        )


# =============================================================================
# Mock Strategy & Research Agents
# =============================================================================


class MockBullishResearcher(MockBaseAgent):
    """Mock Bullish Researcher that returns deterministic data."""

    def __init__(self):
        super().__init__(
            role=AgentRole.BULLISH_RESEARCHER,
            system_prompt="Mock bullish researcher",
            temperature=0.7,
        )

    async def analyze(self, context: dict[str, Any]) -> AgentReport:
        """Mock analyze method required by base class."""
        return AgentReport(
            agent_role=self.role,
            symbol=context.get("symbol", "TEST"),
            summary="Mock bullish analysis",
            confidence=0.8,
        )

    async def debate(
        self,
        context: dict[str, Any],
        round_number: int,
        previous_arguments: list[DebateArgument] = None,
    ) -> DebateArgument:
        """Return mock bullish argument."""
        return DebateArgument(
            agent_role=AgentRole.BULLISH_RESEARCHER,
            round_number=round_number,
            argument="Strong fundamentals support upward price movement",
            supporting_evidence=["High profit margins", "Growing revenue", "Positive sentiment"],
            confidence=0.8,
        )


class MockBearishResearcher(MockBaseAgent):
    """Mock Bearish Researcher that returns deterministic data."""

    def __init__(self):
        super().__init__(
            role=AgentRole.BEARISH_RESEARCHER,
            system_prompt="Mock bearish researcher",
            temperature=0.7,
        )

    async def analyze(self, context: dict[str, Any]) -> AgentReport:
        """Mock analyze method required by base class."""
        return AgentReport(
            agent_role=self.role,
            symbol=context.get("symbol", "TEST"),
            summary="Mock bearish analysis",
            confidence=0.7,
        )

    async def debate(
        self,
        context: dict[str, Any],
        round_number: int,
        previous_arguments: list[DebateArgument] = None,
    ) -> DebateArgument:
        """Return mock bearish argument."""
        return DebateArgument(
            agent_role=AgentRole.BEARISH_RESEARCHER,
            round_number=round_number,
            argument="Valuation metrics suggest overvaluation concerns",
            supporting_evidence=["High P/E ratio", "Market saturation", "Regulatory risks"],
            confidence=0.7,
        )


class MockDerivativesStrategist(MockBaseAgent):
    """Mock Derivatives Strategist that returns deterministic data."""

    def __init__(self):
        super().__init__(
            role=AgentRole.DERIVATIVES_STRATEGIST,
            system_prompt="Mock derivatives strategist",
            temperature=0.6,
        )

    async def analyze(self, context: dict[str, Any]) -> AgentReport:
        """Mock analyze method required by base class."""
        return AgentReport(
            agent_role=self.role,
            symbol=context.get("symbol", "TEST"),
            summary="Mock derivatives strategy analysis",
            confidence=0.75,
        )

    async def propose_strategy(self, context: dict[str, Any]) -> StrategyProposal:
        """Return mock strategy proposal."""
        symbol = context.get("symbol", "TEST")
        
        return StrategyProposal(
            symbol=symbol,
            strategy_type=StrategyType.COVERED_CALL,
            direction=TradeDirection.LONG,
            rationale="Generate income while maintaining long exposure",
            expected_return=8.5,
            max_loss=-15.0,
            holding_period="30-45 days",
            entry_criteria=["Price above 190", "RSI between 50-70"],
            exit_criteria=["Target profit reached", "Technical breakdown"],
            risk_factors=["Market volatility", "Earnings announcement"],
            confidence=0.75,
        )


# =============================================================================
# Mock Execution Agents
# =============================================================================


class MockEquityTrader(MockBaseAgent):
    """Mock Equity Trader that returns deterministic data."""

    def __init__(self):
        super().__init__(
            role=AgentRole.EQUITY_TRADER,
            system_prompt="Mock equity trader",
            temperature=0.5,
        )

    async def analyze(self, context: dict[str, Any]) -> AgentReport:
        """Mock analyze method required by base class."""
        return AgentReport(
            agent_role=self.role,
            symbol=context.get("symbol", "TEST"),
            summary="Mock equity execution analysis",
            confidence=0.8,
        )

    async def create_execution_plan(self, context: dict[str, Any]) -> ExecutionPlan:
        """Return mock execution plan for equity trades."""
        symbol = context.get("symbol", "TEST")
        
        return ExecutionPlan(
            symbol=symbol,
            strategy_type=StrategyType.LONG_EQUITY,
            orders=[
                Order(
                    symbol=symbol,
                    side=OrderSide.BUY,
                    quantity=100,
                    order_type=OrderType.LIMIT,
                    price=195.00,
                )
            ],
            estimated_cost=19500.00,
            estimated_slippage=25.00,
            timing_recommendation="Execute during market hours, split into 2-3 orders",
        )


class MockFnOTrader(MockBaseAgent):
    """Mock F&O Trader that returns deterministic data."""

    def __init__(self):
        super().__init__(
            role=AgentRole.FNO_TRADER,
            system_prompt="Mock fno trader",
            temperature=0.5,
        )

    async def analyze(self, context: dict[str, Any]) -> AgentReport:
        """Mock analyze method required by base class."""
        return AgentReport(
            agent_role=self.role,
            symbol=context.get("symbol", "TEST"),
            summary="Mock F&O execution analysis",
            confidence=0.8,
        )

    async def create_execution_plan(self, context: dict[str, Any]) -> ExecutionPlan:
        """Return mock execution plan for F&O trades."""
        symbol = context.get("symbol", "TEST")
        
        return ExecutionPlan(
            symbol=symbol,
            strategy_type=StrategyType.COVERED_CALL,
            orders=[
                Order(
                    symbol=symbol,
                    side=OrderSide.BUY,
                    quantity=100,
                    order_type=OrderType.LIMIT,
                    price=195.00,
                ),
                Order(
                    symbol=symbol,
                    side=OrderSide.SELL,
                    quantity=1,
                    order_type=OrderType.LIMIT,
                    price=3.50,
                    expiry="2024-02-16",
                    strike=200.0,
                    option_type="call",
                ),
            ],
            estimated_cost=19150.00,
            estimated_slippage=35.00,
            timing_recommendation="Execute equity first, then options",
        )


# =============================================================================
# Mock Oversight Agents
# =============================================================================


class MockRiskManager(MockCriticalAgent):
    """Mock Risk Manager that returns deterministic data."""

    def __init__(self):
        super().__init__(
            role=AgentRole.RISK_MANAGER,
            system_prompt="Mock risk manager",
            temperature=0.4,
        )

    async def analyze(self, context: dict[str, Any]) -> AgentReport:
        """Mock analyze method required by base class."""
        return AgentReport(
            agent_role=self.role,
            symbol=context.get("symbol", "TEST"),
            summary="Mock risk analysis",
            confidence=0.8,
        )

    async def assess_risk(self, context: dict[str, Any]) -> RiskAssessment:
        """Return mock risk assessment."""
        symbol = context.get("symbol", "TEST")
        approved = context.get("should_approve", True)  # Allow control in tests
        
        return RiskAssessment(
            symbol=symbol,
            approved=approved,
            var_estimate=1500.00,
            position_size_pct=4.5,
            sector_exposure="Technology: 15%",
            risk_warnings=["High concentration in tech sector"] if approved else ["Excessive risk"],
            recommendation="Approved with position size limit" if approved else "Rejected - risk too high",
        )


class MockPortfolioManager(MockCriticalAgent):
    """Mock Portfolio Manager that returns deterministic data."""

    def __init__(self):
        super().__init__(
            role=AgentRole.PORTFOLIO_MANAGER,
            system_prompt="Mock portfolio manager",
            temperature=0.4,
        )

    async def analyze(self, context: dict[str, Any]) -> AgentReport:
        """Mock analyze method required by base class."""
        return AgentReport(
            agent_role=self.role,
            symbol=context.get("symbol", "TEST"),
            summary="Mock portfolio analysis",
            confidence=0.8,
        )

    async def make_decision(self, context: dict[str, Any]) -> PortfolioDecision:
        """Return mock portfolio decision."""
        symbol = context.get("symbol", "TEST")
        
        # Check if risk assessment approved
        risk_assessment = context.get("risk_assessment")
        approved = risk_assessment.approved if risk_assessment else True
        
        return PortfolioDecision(
            symbol=symbol,
            approved=approved,
            decision_rationale="Strategy aligns with portfolio objectives" if approved else "Risk concerns",
            position_size=5000.00 if approved else 0.0,
            monitoring_requirements=["Daily price checks", "Volatility monitoring"] if approved else [],
            conditions=["Exit if stop loss triggered"] if approved else [],
        )


class MockReflectiveAgent(MockCriticalAgent):
    """Mock Reflective Agent that returns deterministic data."""

    def __init__(self):
        super().__init__(
            role=AgentRole.REFLECTIVE_AGENT,
            system_prompt="Mock reflective agent",
            temperature=0.6,
        )

    async def analyze(self, context: dict[str, Any]) -> AgentReport:
        """Mock analyze method required by base class."""
        return AgentReport(
            agent_role=self.role,
            symbol=context.get("symbol", "TEST"),
            summary="Mock reflection analysis",
            confidence=0.8,
        )

    async def reflect(self, context: dict[str, Any]) -> dict[str, Any]:
        """Return mock reflection on trade outcome."""
        return {
            "success_factors": ["Good timing", "Accurate analysis"],
            "failure_factors": [],
            "lessons_learned": ["Market timing is critical"],
            "strategy_adjustments": ["Increase position size threshold"],
            "confidence_adjustment": 0.05,
        }
