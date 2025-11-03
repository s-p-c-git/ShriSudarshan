"""Unit tests for MarketDataProvider."""

from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.data.providers.market_data import MarketDataProvider


class TestMarketDataProvider:
    """Test suite for MarketDataProvider."""

    def test_initialization(self):
        """Test provider initialization."""
        provider = MarketDataProvider()
        assert provider._cache == {}

    @patch("src.data.providers.market_data.yf.Ticker")
    def test_get_price_history(self, mock_ticker):
        """Test getting price history."""
        # Mock data
        mock_history = pd.DataFrame(
            {
                "Open": [150.0, 151.0, 152.0],
                "High": [152.0, 153.0, 154.0],
                "Low": [149.0, 150.0, 151.0],
                "Close": [151.0, 152.0, 153.0],
                "Volume": [1000000, 1100000, 1200000],
            }
        )

        mock_instance = Mock()
        mock_instance.history.return_value = mock_history
        mock_ticker.return_value = mock_instance

        # Test
        provider = MarketDataProvider()
        history = provider.get_price_history("AAPL", period="1mo", interval="1d")

        assert not history.empty
        assert len(history) == 3
        assert "Close" in history.columns
        mock_instance.history.assert_called_once_with(period="1mo", interval="1d")

    @patch("src.data.providers.market_data.yf.Ticker")
    def test_get_price_history_error(self, mock_ticker):
        """Test price history with error handling."""
        mock_ticker.side_effect = Exception("API Error")

        provider = MarketDataProvider()
        history = provider.get_price_history("INVALID")

        assert history.empty

    @patch("src.data.providers.market_data.yf.Ticker")
    def test_get_current_price(self, mock_ticker):
        """Test getting current price."""
        mock_instance = Mock()
        mock_instance.info = {"currentPrice": 195.50}
        mock_ticker.return_value = mock_instance

        provider = MarketDataProvider()
        price = provider.get_current_price("AAPL")

        assert price == 195.50

    @patch("src.data.providers.market_data.yf.Ticker")
    def test_get_current_price_fallback(self, mock_ticker):
        """Test current price with fallback to regularMarketPrice."""
        mock_instance = Mock()
        mock_instance.info = {"regularMarketPrice": 195.50}
        mock_ticker.return_value = mock_instance

        provider = MarketDataProvider()
        price = provider.get_current_price("AAPL")

        assert price == 195.50

    @patch("src.data.providers.market_data.yf.Ticker")
    def test_get_current_price_error(self, mock_ticker):
        """Test current price error handling."""
        mock_ticker.side_effect = Exception("API Error")

        provider = MarketDataProvider()
        price = provider.get_current_price("INVALID")

        assert price is None

    @patch("src.data.providers.market_data.yf.Ticker")
    def test_get_fundamentals(self, mock_ticker):
        """Test getting fundamental data."""
        mock_instance = Mock()
        mock_instance.info = {
            "longName": "Apple Inc.",
            "sector": "Technology",
            "marketCap": 3000000000000,
            "totalRevenue": 394328000000,
            "trailingPE": 28.5,
            "priceToBook": 45.2,
            "currentPrice": 195.50,
        }
        mock_ticker.return_value = mock_instance

        provider = MarketDataProvider()
        fundamentals = provider.get_fundamentals("AAPL")

        assert fundamentals["symbol"] == "AAPL"
        assert fundamentals["company_name"] == "Apple Inc."
        assert fundamentals["sector"] == "Technology"
        assert fundamentals["pe_ratio"] == 28.5
        assert fundamentals["current_price"] == 195.50

    @patch("src.data.providers.market_data.yf.Ticker")
    def test_get_fundamentals_error(self, mock_ticker):
        """Test fundamentals error handling."""
        mock_ticker.side_effect = Exception("API Error")

        provider = MarketDataProvider()
        fundamentals = provider.get_fundamentals("INVALID")

        assert "error" in fundamentals
        assert fundamentals["symbol"] == "INVALID"

    @patch("src.data.providers.market_data.yf.Ticker")
    def test_get_financial_statements(self, mock_ticker):
        """Test getting financial statements."""
        mock_instance = Mock()
        mock_instance.financials = pd.DataFrame({"Revenue": [100, 110, 120]})
        mock_instance.balance_sheet = pd.DataFrame({"Assets": [500, 550, 600]})
        mock_instance.cashflow = pd.DataFrame({"Cash": [50, 60, 70]})
        mock_instance.quarterly_financials = pd.DataFrame()
        mock_instance.quarterly_balance_sheet = pd.DataFrame()
        mock_instance.quarterly_cashflow = pd.DataFrame()
        mock_ticker.return_value = mock_instance

        provider = MarketDataProvider()
        statements = provider.get_financial_statements("AAPL")

        assert "income_statement" in statements
        assert "balance_sheet" in statements
        assert "cash_flow" in statements
        assert not statements["income_statement"].empty

    @patch("src.data.providers.market_data.yf.Ticker")
    def test_get_options_chain(self, mock_ticker):
        """Test getting options chain."""
        mock_calls = pd.DataFrame(
            {
                "strike": [190.0, 195.0, 200.0],
                "lastPrice": [5.50, 3.50, 1.50],
            }
        )
        mock_puts = pd.DataFrame(
            {
                "strike": [190.0, 195.0, 200.0],
                "lastPrice": [1.50, 3.50, 5.50],
            }
        )

        mock_option_chain = Mock()
        mock_option_chain.calls = mock_calls
        mock_option_chain.puts = mock_puts

        mock_instance = Mock()
        mock_instance.options = ["2024-02-16", "2024-03-15"]
        mock_instance.option_chain.return_value = mock_option_chain
        mock_ticker.return_value = mock_instance

        provider = MarketDataProvider()
        options = provider.get_options_chain("AAPL")

        assert "calls" in options
        assert "puts" in options
        assert "expiry" in options
        assert len(options["calls"]) == 3

    @patch("src.data.providers.market_data.yf.Ticker")
    def test_get_options_chain_specific_expiry(self, mock_ticker):
        """Test getting options chain with specific expiry."""
        mock_option_chain = Mock()
        mock_option_chain.calls = pd.DataFrame()
        mock_option_chain.puts = pd.DataFrame()

        mock_instance = Mock()
        mock_instance.option_chain.return_value = mock_option_chain
        mock_ticker.return_value = mock_instance

        provider = MarketDataProvider()
        _options = provider.get_options_chain("AAPL", expiry_date="2024-02-16")

        mock_instance.option_chain.assert_called_once_with("2024-02-16")

    @patch("src.data.providers.market_data.yf.Ticker")
    def test_get_available_expiries(self, mock_ticker):
        """Test getting available expiry dates."""
        mock_instance = Mock()
        mock_instance.options = ["2024-02-16", "2024-03-15", "2024-04-19"]
        mock_ticker.return_value = mock_instance

        provider = MarketDataProvider()
        expiries = provider.get_available_expiries("AAPL")

        assert len(expiries) == 3
        assert "2024-02-16" in expiries

    @patch("src.data.providers.market_data.yf.Ticker")
    def test_calculate_technical_indicators(self, mock_ticker):
        """Test calculating technical indicators."""
        # Create price history
        dates = pd.date_range(end=datetime.now(), periods=200, freq="D")
        mock_history = pd.DataFrame(
            {
                "Close": [150 + i * 0.1 for i in range(200)],
                "High": [152 + i * 0.1 for i in range(200)],
                "Low": [148 + i * 0.1 for i in range(200)],
                "Volume": [1000000 + i * 1000 for i in range(200)],
            },
            index=dates,
        )

        mock_instance = Mock()
        mock_instance.history.return_value = mock_history
        mock_ticker.return_value = mock_instance

        provider = MarketDataProvider()
        indicators = provider.calculate_technical_indicators("AAPL")

        # Check that indicators are calculated
        assert "sma_20" in indicators
        assert "sma_50" in indicators
        assert "rsi" in indicators
        assert "macd" in indicators
        assert "current_price" in indicators

        # RSI should be between 0 and 100
        assert 0 <= indicators["rsi"] <= 100

    @patch("src.data.providers.market_data.yf.Ticker")
    def test_calculate_technical_indicators_insufficient_data(self, mock_ticker):
        """Test technical indicators with insufficient data."""
        # Only 10 days of data
        dates = pd.date_range(end=datetime.now(), periods=10, freq="D")
        mock_history = pd.DataFrame(
            {
                "Close": [150 + i for i in range(10)],
                "High": [152 + i for i in range(10)],
                "Low": [148 + i for i in range(10)],
                "Volume": [1000000 + i * 1000 for i in range(10)],
            },
            index=dates,
        )

        mock_instance = Mock()
        mock_instance.history.return_value = mock_history
        mock_ticker.return_value = mock_instance

        provider = MarketDataProvider()
        indicators = provider.calculate_technical_indicators("AAPL")

        # Many indicators should be None due to insufficient data
        assert indicators["sma_20"] is None
        assert indicators["sma_50"] is None
        assert indicators["rsi"] is None

    @patch("src.data.providers.market_data.yf.Ticker")
    def test_calculate_technical_indicators_error(self, mock_ticker):
        """Test technical indicators error handling."""
        mock_ticker.side_effect = Exception("API Error")

        provider = MarketDataProvider()
        indicators = provider.calculate_technical_indicators("INVALID")

        assert indicators == {}

    @patch("src.data.providers.market_data.yf.Ticker")
    def test_get_market_overview(self, mock_ticker):
        """Test getting market overview."""

        def mock_ticker_factory(symbol):
            mock_instance = Mock()
            mock_instance.info = {}

            # Create price history
            dates = pd.date_range(end=datetime.now(), periods=5, freq="D")
            mock_instance.history.return_value = pd.DataFrame(
                {
                    "Close": [4500, 4520, 4510, 4530, 4550],
                },
                index=dates,
            )

            return mock_instance

        mock_ticker.side_effect = mock_ticker_factory

        provider = MarketDataProvider()
        overview = provider.get_market_overview()

        # Should have some indices
        assert isinstance(overview, dict)
        # Keys might vary depending on API success

    @patch("src.data.providers.market_data.yf.Ticker")
    def test_get_market_overview_error(self, mock_ticker):
        """Test market overview error handling."""
        mock_ticker.side_effect = Exception("API Error")

        provider = MarketDataProvider()
        overview = provider.get_market_overview()

        assert overview == {}


class TestMarketDataProviderIntegration:
    """Integration-style tests (require marking for slow tests)."""

    @pytest.mark.skip(reason="Integration test - requires network")
    def test_real_api_call(self):
        """Test with real API call (requires network)."""
        provider = MarketDataProvider()

        # Get current price for a major stock
        price = provider.get_current_price("AAPL")

        # Should return a valid price
        assert price is not None
        assert isinstance(price, float)
        assert price > 0
