"""Test configuration and fixtures for Project Shri Sudarshan."""

import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pandas as pd
import pytest


# Set required environment variables before any imports that use Settings
os.environ.setdefault("OPENAI_API_KEY", "test-key-123")
os.environ.setdefault("PREMIUM_MODEL", "gpt-4o")
os.environ.setdefault("STANDARD_MODEL", "gpt-4o-mini")
os.environ.setdefault("LLM_PROVIDER", "openai")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key-123")

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
    RiskAssessment,
    Sentiment,
    SentimentReport,
    StrategyProposal,
    StrategyType,
    TechnicalReport,
    TradeDirection,
    TrendDirection,
)


# ============================================================================
# Basic Fixtures
# ============================================================================


@pytest.fixture
def sample_symbol():
    """Sample stock symbol for testing."""
    return "AAPL"


@pytest.fixture
def sample_symbols():
    """Multiple sample stock symbols for testing."""
    return ["AAPL", "MSFT", "GOOGL", "TSLA", "SPY"]


@pytest.fixture
def sample_date_range():
    """Sample date range for testing."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
    }


# ============================================================================
# Data Fixtures
# ============================================================================


@pytest.fixture
def sample_price_history():
    """Sample price history DataFrame."""
    dates = pd.date_range(end=datetime.now(), periods=100, freq="D")
    return pd.DataFrame(
        {
            "Open": [150 + i * 0.5 for i in range(100)],
            "High": [152 + i * 0.5 for i in range(100)],
            "Low": [148 + i * 0.5 for i in range(100)],
            "Close": [151 + i * 0.5 for i in range(100)],
            "Volume": [1000000 + i * 10000 for i in range(100)],
        },
        index=dates,
    )


@pytest.fixture
def sample_fundamentals():
    """Sample fundamental data."""
    return {
        "symbol": "AAPL",
        "company_name": "Apple Inc.",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "market_cap": 3000000000000,
        "revenue": 394328000000,
        "net_income": 99803000000,
        "pe_ratio": 28.5,
        "pb_ratio": 45.2,
        "ps_ratio": 7.6,
        "roe": 1.47,
        "roa": 0.28,
        "profit_margin": 0.253,
        "operating_margin": 0.307,
        "debt_to_equity": 1.97,
        "current_ratio": 0.98,
        "quick_ratio": 0.83,
        "dividend_yield": 0.0045,
        "beta": 1.25,
        "current_price": 195.50,
        "target_price": 210.00,
    }


@pytest.fixture
def sample_technical_indicators():
    """Sample technical indicators."""
    return {
        "sma_20": 195.0,
        "sma_50": 190.0,
        "sma_200": 180.0,
        "ema_12": 196.0,
        "ema_26": 192.0,
        "rsi": 65.5,
        "macd": 2.5,
        "macd_signal": 2.0,
        "macd_histogram": 0.5,
        "bb_upper": 205.0,
        "bb_middle": 195.0,
        "bb_lower": 185.0,
        "current_price": 195.50,
        "resistance_levels": [200.0, 205.0, 210.0],
        "support_levels": [190.0, 185.0, 180.0],
    }


@pytest.fixture
def sample_news_articles():
    """Sample news articles."""
    return [
        {
            "title": "Company Reports Strong Quarterly Earnings",
            "publisher": "Financial Times",
            "published": datetime.now() - timedelta(days=1),
            "summary": "Revenue beats expectations with strong growth",
            "sentiment": "positive",
        },
        {
            "title": "Market Volatility Concerns Rise",
            "publisher": "Reuters",
            "published": datetime.now() - timedelta(days=2),
            "summary": "Uncertainty in global markets causes concern",
            "sentiment": "negative",
        },
    ]


# ============================================================================
# Agent Report Fixtures
# ============================================================================


@pytest.fixture
def sample_fundamentals_report(sample_symbol):
    """Sample fundamentals analyst report."""
    return FundamentalsReport(
        symbol=sample_symbol,
        summary="Strong fundamentals with solid profitability metrics",
        confidence=0.8,
        revenue=394328000000,
        net_income=99803000000,
        pe_ratio=28.5,
        pb_ratio=45.2,
        roe=1.47,
        intrinsic_value=210.00,
        current_price=195.50,
        investment_thesis=Sentiment.BULLISH,
    )


@pytest.fixture
def sample_macro_news_report(sample_symbol):
    """Sample macro/news analyst report."""
    return MacroNewsReport(
        symbol=sample_symbol,
        summary="Positive market conditions with supportive monetary policy",
        confidence=0.7,
        market_sentiment=Sentiment.BULLISH,
        key_events=["Fed maintains rates", "Strong GDP growth"],
        economic_indicators={"gdp_growth": 2.5, "inflation": 2.1},
    )


@pytest.fixture
def sample_sentiment_report(sample_symbol):
    """Sample sentiment analyst report."""
    return SentimentReport(
        symbol=sample_symbol,
        summary="Positive social sentiment with increasing retail interest",
        confidence=0.75,
        social_sentiment=Sentiment.BULLISH,
        sentiment_score=0.65,
        volume_trend="increasing",
        retail_interest="high",
    )


@pytest.fixture
def sample_technical_report(sample_symbol):
    """Sample technical analyst report."""
    return TechnicalReport(
        symbol=sample_symbol,
        summary="Strong uptrend with bullish indicators",
        confidence=0.85,
        trend_direction=TrendDirection.UPTREND,
        support_levels=[190.0, 185.0, 180.0],
        resistance_levels=[200.0, 205.0, 210.0],
        chart_patterns=["ascending triangle", "golden cross"],
        indicators={"rsi": 65.5, "macd": "bullish"},
    )


@pytest.fixture
def sample_analyst_reports(
    sample_fundamentals_report,
    sample_macro_news_report,
    sample_sentiment_report,
    sample_technical_report,
):
    """Complete set of analyst reports."""
    return {
        "fundamentals": sample_fundamentals_report,
        "macro_news": sample_macro_news_report,
        "sentiment": sample_sentiment_report,
        "technical": sample_technical_report,
    }


@pytest.fixture
def sample_debate_arguments(sample_symbol):
    """Sample debate arguments."""
    return [
        DebateArgument(
            agent_role=AgentRole.BULLISH_RESEARCHER,
            stance=Sentiment.BULLISH,
            rationale="Strong fundamentals support upward price movement",
            supporting_evidence=["High profit margins", "Growing revenue"],
            confidence=0.8,
        ),
        DebateArgument(
            agent_role=AgentRole.BEARISH_RESEARCHER,
            stance=Sentiment.BEARISH,
            rationale="Valuation metrics suggest overvaluation",
            supporting_evidence=["High P/E ratio", "Market saturation"],
            confidence=0.7,
        ),
    ]


@pytest.fixture
def sample_strategy_proposal(sample_symbol):
    """Sample strategy proposal."""
    return StrategyProposal(
        symbol=sample_symbol,
        strategy_type=StrategyType.COVERED_CALL,
        direction=TradeDirection.LONG,
        rationale="Generate income while maintaining long exposure",
        expected_return=8.5,
        max_loss=-15.0,
        holding_period="30-45 days",
        entry_criteria=["Price above 190", "RSI between 50-70"],
        exit_criteria=["Target profit reached", "Technical breakdown"],
        confidence=0.75,
    )


@pytest.fixture
def sample_execution_plan(sample_symbol):
    """Sample execution plan."""
    return ExecutionPlan(
        symbol=sample_symbol,
        strategy_type=StrategyType.COVERED_CALL,
        orders=[
            Order(
                symbol=sample_symbol,
                side=OrderSide.BUY,
                quantity=100,
                order_type=OrderType.LIMIT,
                price=195.00,
            ),
            Order(
                symbol=sample_symbol,
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
        estimated_slippage=25.00,
        timing_recommendation="Execute during market hours",
    )


@pytest.fixture
def sample_risk_assessment(sample_symbol):
    """Sample risk assessment."""
    return RiskAssessment(
        symbol=sample_symbol,
        approved=True,
        var_estimate=1500.00,
        position_size_pct=4.5,
        sector_exposure="Technology: 15%",
        risk_warnings=["High concentration in tech sector"],
        recommendation="Approved with position size limit",
    )


@pytest.fixture
def sample_portfolio_decision(sample_symbol):
    """Sample portfolio decision."""
    return PortfolioDecision(
        symbol=sample_symbol,
        approved=True,
        decision_rationale="Strategy aligns with portfolio objectives",
        position_size=5000.00,
        monitoring_requirements=["Daily price checks", "Volatility monitoring"],
    )


# ============================================================================
# Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_market_data_provider(
    sample_price_history, sample_fundamentals, sample_technical_indicators
):
    """Mock MarketDataProvider."""
    mock_provider = Mock()
    mock_provider.get_price_history.return_value = sample_price_history
    mock_provider.get_current_price.return_value = 195.50
    mock_provider.get_fundamentals.return_value = sample_fundamentals
    mock_provider.calculate_technical_indicators.return_value = sample_technical_indicators
    mock_provider.get_options_chain.return_value = {
        "calls": pd.DataFrame(),
        "puts": pd.DataFrame(),
    }
    mock_provider.get_available_expiries.return_value = ["2024-02-16", "2024-03-15"]
    return mock_provider


@pytest.fixture
def mock_news_provider(sample_news_articles):
    """Mock NewsProvider."""
    mock_provider = Mock()
    mock_provider.get_company_news.return_value = sample_news_articles
    mock_provider.get_market_news.return_value = sample_news_articles
    mock_provider.aggregate_sentiment.return_value = {
        "sentiment_score": 0.65,
        "sentiment_label": "bullish",
        "article_count": 10,
        "positive_count": 7,
        "negative_count": 2,
        "neutral_count": 1,
    }
    return mock_provider


@pytest.fixture
def mock_llm():
    """Mock LLM for testing agents."""
    mock = AsyncMock()
    mock_response = Mock()
    mock_response.content = "Sample LLM response"
    mock.ainvoke.return_value = mock_response
    return mock


# ============================================================================
# Context Fixtures
# ============================================================================


@pytest.fixture
def sample_context(sample_symbol, mock_market_data_provider, mock_news_provider):
    """Sample context for agent testing."""
    return {
        "symbol": sample_symbol,
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "market_data_provider": mock_market_data_provider,
        "news_provider": mock_news_provider,
    }


@pytest.fixture
def sample_workflow_state(sample_symbol, sample_analyst_reports):
    """Sample workflow state."""
    return {
        "symbol": sample_symbol,
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "current_phase": "analysis",
        "analyst_reports": sample_analyst_reports,
        "debate_arguments": [],
        "strategy_proposal": None,
        "execution_plan": None,
        "risk_assessment": None,
        "portfolio_decision": None,
        "errors": [],
    }


# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture
def test_env_vars(monkeypatch):
    """Set test environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    monkeypatch.setenv("PREMIUM_MODEL", "gpt-4o")
    monkeypatch.setenv("STANDARD_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("MAX_POSITION_SIZE", "0.05")
    monkeypatch.setenv("MAX_PORTFOLIO_RISK", "0.02")
    monkeypatch.setenv("ENABLE_CONCURRENT_ANALYSIS", "false")
    monkeypatch.setenv("MAX_DEBATE_ROUNDS", "2")


# ============================================================================
# Mock Agent Fixtures
# ============================================================================


@pytest.fixture
def mock_fundamentals_analyst():
    """Mock FundamentalsAnalyst for testing."""
    from tests.mock_agents import MockFundamentalsAnalyst

    return MockFundamentalsAnalyst()


@pytest.fixture
def mock_technical_analyst():
    """Mock TechnicalAnalyst for testing."""
    from tests.mock_agents import MockTechnicalAnalyst

    return MockTechnicalAnalyst()


@pytest.fixture
def mock_sentiment_analyst():
    """Mock SentimentAnalyst for testing."""
    from tests.mock_agents import MockSentimentAnalyst

    return MockSentimentAnalyst()


@pytest.fixture
def mock_macro_news_analyst():
    """Mock MacroNewsAnalyst for testing."""
    from tests.mock_agents import MockMacroNewsAnalyst

    return MockMacroNewsAnalyst()


@pytest.fixture
def mock_bullish_researcher():
    """Mock BullishResearcher for testing."""
    from tests.mock_agents import MockBullishResearcher

    return MockBullishResearcher()


@pytest.fixture
def mock_bearish_researcher():
    """Mock BearishResearcher for testing."""
    from tests.mock_agents import MockBearishResearcher

    return MockBearishResearcher()


@pytest.fixture
def mock_derivatives_strategist():
    """Mock DerivativesStrategist for testing."""
    from tests.mock_agents import MockDerivativesStrategist

    return MockDerivativesStrategist()


@pytest.fixture
def mock_equity_trader():
    """Mock EquityTrader for testing."""
    from tests.mock_agents import MockEquityTrader

    return MockEquityTrader()


@pytest.fixture
def mock_fno_trader():
    """Mock FnOTrader for testing."""
    from tests.mock_agents import MockFnOTrader

    return MockFnOTrader()


@pytest.fixture
def mock_risk_manager():
    """Mock RiskManager for testing."""
    from tests.mock_agents import MockRiskManager

    return MockRiskManager()


@pytest.fixture
def mock_portfolio_manager():
    """Mock PortfolioManager for testing."""
    from tests.mock_agents import MockPortfolioManager

    return MockPortfolioManager()


@pytest.fixture
def mock_reflective_agent():
    """Mock ReflectiveAgent for testing."""
    from tests.mock_agents import MockReflectiveAgent

    return MockReflectiveAgent()
