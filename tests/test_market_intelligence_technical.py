# tests/test_market_intelligence_technical.py
"""
Tests for TechnicalAnalyst market intelligence agent.

These tests verify technical indicator calculations and chart pattern detection.
"""
import pytest

# Try to import, skip tests if dependencies missing
pytest.importorskip("yfinance")

import pandas as pd
import numpy as np


@pytest.fixture
def simple_price_series():
    """Simple price series for testing calculations."""
    return [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110]


@pytest.fixture
def sample_price_dataframe():
    """Sample price DataFrame for more complex tests."""
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")

    # Create realistic price movements
    close_prices = 100 + np.cumsum(np.random.randn(100) * 2)
    close_prices = np.maximum(close_prices, 50)  # Keep prices reasonable

    df = pd.DataFrame(
        {
            "Open": close_prices * 0.99,
            "High": close_prices * 1.02,
            "Low": close_prices * 0.98,
            "Close": close_prices,
            "Volume": np.random.randint(1000000, 5000000, 100),
        },
        index=dates,
    )

    return df


def test_technical_module_import():
    """Test that technical module can be imported."""
    from src.agents.market_intelligence import technical

    assert technical is not None


def test_technical_analyst_instantiation():
    """Test that TechnicalAnalyst can be instantiated."""
    from src.agents.market_intelligence.technical import TechnicalAnalyst

    analyst = TechnicalAnalyst()
    assert analyst is not None
    assert hasattr(analyst, "role")


def test_calculate_sma_if_exists(simple_price_series):
    """Test SMA calculation if function exists."""
    from src.agents.market_intelligence import technical

    # If technical module exposes SMA function
    if hasattr(technical, "calculate_sma"):
        sma = technical.calculate_sma(simple_price_series, window=3)
        assert isinstance(sma, (float, list, np.ndarray))

        # If it returns a single value, check it's reasonable
        if isinstance(sma, float):
            assert sma > 0
            assert 100 <= sma <= 110


def test_calculate_rsi_if_exists(simple_price_series):
    """Test RSI calculation if function exists."""
    from src.agents.market_intelligence import technical

    # If technical module exposes RSI function
    if hasattr(technical, "calculate_rsi"):
        rsi = technical.calculate_rsi(simple_price_series, period=14)

        if isinstance(rsi, (float, int)):
            # RSI should be between 0 and 100
            assert 0 <= rsi <= 100


def test_technical_analyst_has_analyze(sample_context):
    """Test that TechnicalAnalyst has analyze method."""
    from src.agents.market_intelligence.technical import TechnicalAnalyst

    analyst = TechnicalAnalyst()
    assert hasattr(analyst, "analyze")


@pytest.mark.asyncio
async def test_technical_analyst_analyze(sample_context):
    """Test TechnicalAnalyst analyze method."""
    from src.agents.market_intelligence.technical import TechnicalAnalyst
    from src.data.schemas import TechnicalReport

    analyst = TechnicalAnalyst()

    if hasattr(analyst, "analyze"):
        report = await analyst.analyze(sample_context)

        # Verify report structure
        assert report is not None
        if isinstance(report, TechnicalReport):
            assert report.symbol == sample_context["symbol"]
            assert hasattr(report, "summary")
            assert hasattr(report, "confidence")


def test_support_resistance_detection(sample_price_dataframe):
    """Test support and resistance level detection."""
    from src.agents.market_intelligence.technical import TechnicalAnalyst

    analyst = TechnicalAnalyst()

    # Check if the analyst has support/resistance detection method
    if hasattr(analyst, "_identify_support_resistance"):
        support, resistance = analyst._identify_support_resistance(sample_price_dataframe)

        # Both should be lists
        assert isinstance(support, list)
        assert isinstance(resistance, list)

        # If we found levels, they should be reasonable prices
        if len(support) > 0:
            assert all(isinstance(s, (int, float)) for s in support)
            assert all(s > 0 for s in support)

        if len(resistance) > 0:
            assert all(isinstance(r, (int, float)) for r in resistance)
            assert all(r > 0 for r in resistance)


def test_chart_pattern_detection(sample_price_dataframe):
    """Test chart pattern detection."""
    from src.agents.market_intelligence.technical import TechnicalAnalyst

    analyst = TechnicalAnalyst()

    # Check if analyst has pattern detection
    if hasattr(analyst, "_detect_chart_patterns"):
        # Add some indicators to the dataframe
        df = sample_price_dataframe.copy()
        df["SMA_20"] = df["Close"].rolling(window=20).mean()
        df["SMA_50"] = df["Close"].rolling(window=50).mean()

        patterns = analyst._detect_chart_patterns(df)

        # Patterns should be a list
        assert isinstance(patterns, list)

        # Each pattern should be a string
        if len(patterns) > 0:
            assert all(isinstance(p, str) for p in patterns)


@pytest.mark.asyncio
async def test_technical_indicators_in_report(sample_context):
    """Test that technical indicators are included in the report."""
    from src.agents.market_intelligence.technical import TechnicalAnalyst
    from src.data.schemas import TechnicalReport

    analyst = TechnicalAnalyst()

    if hasattr(analyst, "analyze"):
        report = await analyst.analyze(sample_context)

        if isinstance(report, TechnicalReport):
            # Check for technical indicators
            assert hasattr(report, "indicators")

            # Check for support and resistance levels
            assert hasattr(report, "support_levels")
            assert hasattr(report, "resistance_levels")

            # These should be lists
            assert isinstance(report.support_levels, list)
            assert isinstance(report.resistance_levels, list)
