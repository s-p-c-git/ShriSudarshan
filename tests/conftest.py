"""Test configuration."""

import pytest


@pytest.fixture
def sample_symbol():
    """Sample stock symbol for testing."""
    return "AAPL"


@pytest.fixture
def sample_context():
    """Sample context for agent testing."""
    return {
        "symbol": "AAPL",
        "financial_data": {
            "revenue": 394328000000,
            "net_income": 99803000000,
            "pe_ratio": 28.5,
        }
    }
