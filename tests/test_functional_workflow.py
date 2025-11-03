"""Functional tests for end-to-end workflow."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from src.orchestration.state import create_initial_state
from src.orchestration.workflow import TradingWorkflow


@pytest.mark.asyncio
class TestWorkflowIntegration:
    """Integration tests for complete workflow execution."""

    @pytest.mark.skip(reason="Requires LLM API key and full system setup")
    async def test_complete_workflow_success(self, sample_symbol):
        """Test complete workflow from analysis to execution."""
        workflow = TradingWorkflow()

        # Run workflow
        final_state = await workflow.run(
            symbol=sample_symbol, start_date="2024-01-01", end_date="2024-01-31"
        )

        # Verify workflow completed
        assert final_state["symbol"] == sample_symbol
        assert final_state["analysis_complete"] is True
        assert final_state["debate_complete"] is True

        # Check if approved or rejected
        if final_state["final_approval"]:
            assert final_state["execution_complete"] is True
        else:
            # If rejected, should have rejection reason
            assert (
                len(final_state["errors"]) > 0
                or final_state["risk_approved"] is False
                or final_state["final_approval"] is False
            )

    @pytest.mark.skip(reason="Requires LLM API key")
    async def test_workflow_risk_rejection(self):
        """Test workflow when risk manager rejects."""
        # This would require mocking the risk manager to reject
        pass

    @pytest.mark.skip(reason="Requires LLM API key")
    async def test_workflow_portfolio_rejection(self):
        """Test workflow when portfolio manager rejects."""
        # This would require mocking the portfolio manager to reject
        pass

    async def test_workflow_state_initialization(self):
        """Test workflow initializes state correctly."""
        _workflow = TradingWorkflow()

        # Create initial state
        state = create_initial_state("AAPL")

        assert state["symbol"] == "AAPL"
        assert state["current_phase"] == "initialization"
        assert state["errors"] == []


@pytest.mark.asyncio
class TestWorkflowPhases:
    """Test individual workflow phases with mocking."""

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for agent responses."""
        mock = AsyncMock()
        mock_response = Mock()
        mock_response.content = """
        {
            "summary": "Analysis complete",
            "confidence": 0.8
        }
        """
        mock.ainvoke.return_value = mock_response
        return mock

    async def test_analysis_phase_structure(self, mock_market_data_provider, mock_news_provider):
        """Test that analysis phase processes correctly with mocked data."""
        _workflow = TradingWorkflow()
        state = create_initial_state("AAPL")

        # This would require mocking all analysts
        # For now, just verify state structure is correct
        assert "analyst_reports" in state
        assert "analysis_complete" in state

    async def test_debate_phase_structure(self):
        """Test debate phase state structure."""
        state = create_initial_state("AAPL")

        assert "debate_arguments" in state
        assert "debate_rounds" in state
        assert "debate_complete" in state

    async def test_strategy_phase_structure(self):
        """Test strategy phase state structure."""
        state = create_initial_state("AAPL")

        assert "strategy_proposal" in state
        assert "strategy_complete" in state

    async def test_execution_planning_phase_structure(self):
        """Test execution planning phase state structure."""
        state = create_initial_state("AAPL")

        assert "execution_plan" in state
        assert "execution_plan_complete" in state


class TestMemoryIntegration:
    """Test memory system integration."""

    def test_working_memory_in_workflow(self):
        """Test working memory integration with workflow."""
        from src.memory.working import WorkingMemory

        memory = WorkingMemory()

        # Store workflow state
        memory.set("workflow_AAPL", {"phase": "analysis", "symbol": "AAPL"})

        # Retrieve it
        state = memory.get("workflow_AAPL")
        assert state["symbol"] == "AAPL"

    def test_episodic_memory_trade_storage(self):
        """Test episodic memory for trade storage."""
        import tempfile

        from src.data.schemas import StrategyType, TradeOutcome
        from src.memory.episodic import EpisodicMemory

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            db_url = f"sqlite:///{temp_file.name}"

        try:
            memory = EpisodicMemory(database_url=db_url)

            trade = TradeOutcome(
                trade_id="TEST-001",
                symbol="AAPL",
                strategy_type=StrategyType.LONG_EQUITY,
                entry_date=datetime.now(),
                entry_price=150.00,
                quantity=100,
                outcome="pending",
            )

            memory.store_trade(trade)
            retrieved = memory.get_trade("TEST-001")

            assert retrieved is not None
            assert retrieved.symbol == "AAPL"
        finally:
            import os

            try:
                os.unlink(temp_file.name)
            except Exception:
                pass


class TestDataProvidersIntegration:
    """Test data providers integration."""

    @pytest.mark.skip(reason="Integration test - requires network")
    def test_market_data_provider_real_api(self):
        """Test market data provider with real API."""
        from src.data.providers.market_data import MarketDataProvider

        provider = MarketDataProvider()
        price = provider.get_current_price("AAPL")

        assert price is not None
        assert isinstance(price, float)
        assert price > 0

    @pytest.mark.skip(reason="Integration test - requires network")
    def test_news_provider_real_api(self):
        """Test news provider with real API."""
        from src.data.providers.news import NewsProvider

        provider = NewsProvider()
        articles = provider.get_company_news("AAPL", days_back=7, max_articles=5)

        assert isinstance(articles, list)

    def test_market_data_provider_mock(self, mock_market_data_provider):
        """Test market data provider with mocking."""
        price = mock_market_data_provider.get_current_price("AAPL")

        assert price == 195.50
        mock_market_data_provider.get_current_price.assert_called_once_with("AAPL")

    def test_news_provider_mock(self, mock_news_provider):
        """Test news provider with mocking."""
        sentiment = mock_news_provider.aggregate_sentiment("AAPL")

        assert sentiment["sentiment_label"] == "bullish"
        assert sentiment["sentiment_score"] == 0.65
