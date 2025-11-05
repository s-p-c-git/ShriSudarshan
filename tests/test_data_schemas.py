"""Unit tests for data schemas."""

from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from src.data.schemas import (
    AgentRole,
    DebateArgument,
    ExecutionPlan,
    FundamentalsReport,
    MacroNewsReport,
    Order,
    OrderSide,
    OrderType,
    PortfolioDecision,
    Reflection,
    RiskAssessment,
    Sentiment,
    SentimentReport,
    StrategyProposal,
    StrategyType,
    TechnicalReport,
    TradeDirection,
    TradeOutcome,
    TrendDirection,
)


class TestEnums:
    """Test enum definitions."""

    def test_agent_role_enum(self):
        """Test AgentRole enum.
        
        Note: Agent count updated from 12 to 14 after FinBERT and FinGPT integration
        (issue #51). The two new agents are:
        - FINBERT_SENTIMENT_ANALYST: Quantitative sentiment analysis
        - FINGPT_GENERATIVE_ANALYST: Qualitative deep-dive analysis
        """
        # Test existing roles
        assert AgentRole.FUNDAMENTALS_ANALYST == "fundamentals_analyst"
        assert AgentRole.PORTFOLIO_MANAGER == "portfolio_manager"
        
        # Test new FinBERT and FinGPT roles
        assert AgentRole.FINBERT_SENTIMENT_ANALYST == "finbert_sentiment_analyst"
        assert AgentRole.FINGPT_GENERATIVE_ANALYST == "fingpt_generative_analyst"
        
        # Updated count: 12 original + 2 new (FinBERT, FinGPT) = 14 total
        assert len(list(AgentRole)) == 14

    def test_sentiment_enum(self):
        """Test Sentiment enum."""
        assert Sentiment.VERY_BULLISH == "very_bullish"
        assert Sentiment.BEARISH == "bearish"
        assert len(list(Sentiment)) == 5

    def test_strategy_type_enum(self):
        """Test StrategyType enum."""
        assert StrategyType.LONG_EQUITY == "long_equity"
        assert StrategyType.COVERED_CALL == "covered_call"
        assert len(list(StrategyType)) == 10


class TestFundamentalsReport:
    """Test FundamentalsReport schema."""

    def test_valid_report(self):
        """Test creating a valid fundamentals report."""
        report = FundamentalsReport(
            symbol="AAPL",
            summary="Strong fundamentals",
            confidence=0.8,
            revenue=394328000000,
            net_income=99803000000,
            pe_ratio=28.5,
            investment_thesis=Sentiment.BULLISH,
        )

        assert report.symbol == "AAPL"
        assert report.confidence == 0.8
        assert report.agent_role == AgentRole.FUNDAMENTALS_ANALYST

    def test_default_values(self):
        """Test default values in report."""
        report = FundamentalsReport(
            symbol="AAPL",
            summary="Test",
        )

        assert report.confidence == 0.5  # Default
        assert report.investment_thesis == Sentiment.NEUTRAL  # Default
        assert isinstance(report.timestamp, datetime)

    def test_confidence_bounds(self):
        """Test confidence value validation."""
        # Valid confidence
        report = FundamentalsReport(symbol="AAPL", summary="Test", confidence=0.5)
        assert report.confidence == 0.5

        # Invalid confidence (too high)
        with pytest.raises(ValidationError):
            FundamentalsReport(symbol="AAPL", summary="Test", confidence=1.5)

        # Invalid confidence (negative)
        with pytest.raises(ValidationError):
            FundamentalsReport(symbol="AAPL", summary="Test", confidence=-0.1)


class TestMacroNewsReport:
    """Test MacroNewsReport schema."""

    def test_valid_report(self):
        """Test creating a valid macro news report."""
        report = MacroNewsReport(
            symbol="SPY",
            summary="Positive market outlook",
            market_sentiment=Sentiment.BULLISH,
            key_events=["Fed decision", "Strong GDP"],
        )

        assert report.symbol == "SPY"
        assert report.market_sentiment == Sentiment.BULLISH
        assert len(report.key_events) == 2

    def test_empty_lists(self):
        """Test reports with empty lists."""
        report = MacroNewsReport(
            symbol="SPY",
            summary="Test",
        )

        assert report.key_events == []
        assert report.geopolitical_risks == []


class TestSentimentReport:
    """Test SentimentReport schema."""

    def test_valid_report(self):
        """Test creating a valid sentiment report."""
        report = SentimentReport(
            symbol="TSLA",
            summary="High retail interest",
            social_sentiment=Sentiment.VERY_BULLISH,
            sentiment_score=0.75,
        )

        assert report.sentiment_score == 0.75
        assert report.social_sentiment == Sentiment.VERY_BULLISH

    def test_sentiment_score_bounds(self):
        """Test sentiment score validation."""
        # Valid scores
        SentimentReport(symbol="TSLA", summary="Test", sentiment_score=-1.0)
        SentimentReport(symbol="TSLA", summary="Test", sentiment_score=0.0)
        SentimentReport(symbol="TSLA", summary="Test", sentiment_score=1.0)

        # Invalid scores
        with pytest.raises(ValidationError):
            SentimentReport(symbol="TSLA", summary="Test", sentiment_score=1.5)

        with pytest.raises(ValidationError):
            SentimentReport(symbol="TSLA", summary="Test", sentiment_score=-1.5)


class TestTechnicalReport:
    """Test TechnicalReport schema."""

    def test_valid_report(self):
        """Test creating a valid technical report."""
        report = TechnicalReport(
            symbol="GOOGL",
            summary="Strong uptrend",
            trend_direction=TrendDirection.UPTREND,
            support_levels=[100.0, 95.0, 90.0],
            resistance_levels=[110.0, 115.0, 120.0],
        )

        assert report.trend_direction == TrendDirection.UPTREND
        assert len(report.support_levels) == 3
        assert len(report.resistance_levels) == 3


class TestDebateArgument:
    """Test DebateArgument schema."""

    def test_valid_argument(self):
        """Test creating a valid debate argument."""
        arg = DebateArgument(
            agent_role=AgentRole.BULLISH_RESEARCHER,
            round_number=1,
            argument="Strong buy signal",
            supporting_evidence=["High momentum", "Positive fundamentals"],
            confidence=0.85,
        )

        assert arg.round_number == 1
        assert len(arg.supporting_evidence) == 2
        assert arg.confidence == 0.85

    def test_timestamp_auto_generated(self):
        """Test that timestamp is auto-generated."""
        arg = DebateArgument(
            agent_role=AgentRole.BULLISH_RESEARCHER,
            round_number=1,
            argument="Test",
        )

        assert isinstance(arg.timestamp, datetime)


class TestStrategyProposal:
    """Test StrategyProposal schema."""

    def test_valid_proposal(self):
        """Test creating a valid strategy proposal."""
        proposal = StrategyProposal(
            symbol="MSFT",
            strategy_type=StrategyType.COVERED_CALL,
            direction=TradeDirection.LONG,
            rationale="Generate income",
            expected_return=8.5,
            max_loss=-15.0,
            holding_period="30-45 days",
        )

        assert proposal.strategy_type == StrategyType.COVERED_CALL
        assert proposal.expected_return == 8.5
        assert proposal.max_loss == -15.0

    def test_all_fields(self):
        """Test proposal with all fields populated."""
        proposal = StrategyProposal(
            symbol="MSFT",
            strategy_type=StrategyType.BULL_CALL_SPREAD,
            direction=TradeDirection.LONG,
            rationale="Bullish with limited risk",
            expected_return=25.0,
            max_loss=-5.0,
            holding_period="30 days",
            entry_criteria=["RSI > 50", "Price > SMA"],
            exit_criteria=["Target reached", "Stop loss hit"],
            risk_factors=["Volatility risk", "Time decay"],
            confidence=0.75,
        )

        assert len(proposal.entry_criteria) == 2
        assert len(proposal.exit_criteria) == 2
        assert len(proposal.risk_factors) == 2


class TestOrder:
    """Test Order schema."""

    def test_equity_order(self):
        """Test creating an equity order."""
        order = Order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.LIMIT,
            price=150.00,
        )

        assert order.symbol == "AAPL"
        assert order.quantity == 100
        assert order.price == 150.00

    def test_options_order(self):
        """Test creating an options order."""
        order = Order(
            symbol="AAPL",
            side=OrderSide.SELL,
            quantity=1,
            order_type=OrderType.LIMIT,
            price=3.50,
            expiry="2024-02-16",
            strike=155.0,
            option_type="call",
        )

        assert order.expiry == "2024-02-16"
        assert order.strike == 155.0
        assert order.option_type == "call"

    def test_quantity_validation(self):
        """Test quantity must be positive."""
        # Valid quantity
        Order(symbol="AAPL", side=OrderSide.BUY, quantity=1, order_type=OrderType.MARKET)

        # Invalid quantity (zero)
        with pytest.raises(ValidationError):
            Order(
                symbol="AAPL",
                side=OrderSide.BUY,
                quantity=0,
                order_type=OrderType.MARKET,
            )

        # Invalid quantity (negative)
        with pytest.raises(ValidationError):
            Order(
                symbol="AAPL",
                side=OrderSide.BUY,
                quantity=-10,
                order_type=OrderType.MARKET,
            )


class TestExecutionPlan:
    """Test ExecutionPlan schema."""

    def test_valid_plan(self):
        """Test creating a valid execution plan."""
        orders = [
            Order(
                symbol="AAPL",
                side=OrderSide.BUY,
                quantity=100,
                order_type=OrderType.LIMIT,
                price=150.00,
            ),
            Order(
                symbol="AAPL",
                side=OrderSide.SELL,
                quantity=1,
                order_type=OrderType.LIMIT,
                price=3.50,
                expiry="2024-02-16",
                strike=155.0,
                option_type="call",
            ),
        ]

        plan = ExecutionPlan(
            symbol="AAPL",
            strategy_type=StrategyType.COVERED_CALL,
            orders=orders,
            estimated_cost=14650.00,
            estimated_slippage=25.00,
        )

        assert len(plan.orders) == 2
        assert plan.estimated_cost == 14650.00

    def test_empty_orders(self):
        """Test execution plan can have empty orders list."""
        plan = ExecutionPlan(
            symbol="AAPL",
            strategy_type=StrategyType.LONG_EQUITY,
            orders=[],
            estimated_cost=0.0,
        )

        assert plan.orders == []


class TestRiskAssessment:
    """Test RiskAssessment schema."""

    def test_approved_assessment(self):
        """Test creating an approved risk assessment."""
        assessment = RiskAssessment(
            symbol="AAPL",
            approved=True,
            var_estimate=1500.00,
            position_size_pct=4.5,
            recommendation="Approved with limits",
        )

        assert assessment.approved is True
        assert assessment.var_estimate == 1500.00

    def test_rejected_assessment(self):
        """Test creating a rejected risk assessment."""
        assessment = RiskAssessment(
            symbol="AAPL",
            approved=False,
            var_estimate=5000.00,
            position_size_pct=15.0,
            risk_warnings=["Exceeds position size limit", "High volatility"],
            recommendation="Rejected - too risky",
        )

        assert assessment.approved is False
        assert len(assessment.risk_warnings) == 2


class TestPortfolioDecision:
    """Test PortfolioDecision schema."""

    def test_approved_decision(self):
        """Test creating an approved portfolio decision."""
        decision = PortfolioDecision(
            symbol="AAPL",
            approved=True,
            decision_rationale="Aligns with strategy",
            position_size=5000.00,
            monitoring_requirements=["Daily check", "Volatility monitoring"],
        )

        assert decision.approved is True
        assert decision.position_size == 5000.00
        assert len(decision.monitoring_requirements) == 2

    def test_rejected_decision(self):
        """Test creating a rejected portfolio decision."""
        decision = PortfolioDecision(
            symbol="AAPL",
            approved=False,
            decision_rationale="Market conditions unfavorable",
            position_size=0.0,
            conditions=["Wait for better entry", "Monitor technicals"],
        )

        assert decision.approved is False
        assert decision.position_size == 0.0


class TestTradeOutcome:
    """Test TradeOutcome schema."""

    def test_pending_outcome(self):
        """Test creating a pending trade outcome."""
        outcome = TradeOutcome(
            trade_id="TRADE-001",
            symbol="AAPL",
            strategy_type=StrategyType.LONG_EQUITY,
            entry_date=datetime.now(),
            entry_price=150.00,
            quantity=100,
        )

        assert outcome.outcome == "pending"
        assert outcome.exit_price is None

    def test_completed_outcome(self):
        """Test creating a completed trade outcome."""
        entry_date = datetime.now()
        exit_date = entry_date + timedelta(days=30)

        outcome = TradeOutcome(
            trade_id="TRADE-001",
            symbol="AAPL",
            strategy_type=StrategyType.LONG_EQUITY,
            entry_date=entry_date,
            exit_date=exit_date,
            entry_price=150.00,
            exit_price=165.00,
            quantity=100,
            realized_pnl=1500.00,
            return_pct=10.0,
            outcome="win",
        )

        assert outcome.outcome == "win"
        assert outcome.realized_pnl == 1500.00
        assert outcome.return_pct == 10.0


class TestReflection:
    """Test Reflection schema."""

    def test_valid_reflection(self):
        """Test creating a valid reflection."""
        reflection = Reflection(
            trade_id="TRADE-001",
            symbol="AAPL",
            analysis_summary="Trade executed well with good entry timing",
            what_worked=["Technical analysis", "Patient entry"],
            what_failed=["Exit timing could be better"],
            lessons_learned=["Use trailing stops"],
            strategic_recommendations=["Increase position size for high confidence trades"],
        )

        assert reflection.trade_id == "TRADE-001"
        assert len(reflection.what_worked) == 2
        assert len(reflection.what_failed) == 1
        assert len(reflection.lessons_learned) == 1

    def test_empty_lists(self):
        """Test reflection with empty lists."""
        reflection = Reflection(
            trade_id="TRADE-001",
            symbol="AAPL",
            analysis_summary="Basic reflection",
        )

        assert reflection.what_worked == []
        assert reflection.what_failed == []
        assert reflection.lessons_learned == []
        assert reflection.strategic_recommendations == []
