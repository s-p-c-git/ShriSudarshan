"""Market data provider using yfinance."""

from typing import Any, Optional

import pandas as pd
import yfinance as yf

from src.utils.logger import get_logger


logger = get_logger(__name__)


class MarketDataProvider:
    """Provider for market data using yfinance."""

    def __init__(self):
        """Initialize the market data provider."""
        self._cache: dict[str, Any] = {}
        logger.info("MarketDataProvider initialized")

    def get_price_history(
        self, symbol: str, period: str = "1y", interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Get price history for a symbol.

        Args:
            symbol: Stock symbol
            period: Time period (e.g., "1d", "5d", "1mo", "1y")
            interval: Data interval (e.g., "1m", "5m", "1h", "1d")

        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period=period, interval=interval)
            logger.info(
                "Retrieved price history",
                symbol=symbol,
                period=period,
                rows=len(history),
            )
            return history
        except Exception as e:
            logger.error("Failed to get price history", symbol=symbol, error=str(e))
            return pd.DataFrame()

    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Current price or None if unavailable
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Try multiple price fields
            price = info.get("currentPrice") or info.get("regularMarketPrice")

            if price:
                logger.info("Retrieved current price", symbol=symbol, price=price)
                return float(price)

            logger.warning("No price found", symbol=symbol)
            return None

        except Exception as e:
            logger.error("Failed to get current price", symbol=symbol, error=str(e))
            return None

    def get_fundamentals(self, symbol: str) -> dict[str, Any]:
        """
        Get fundamental data for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with fundamental data
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            fundamentals = {
                "symbol": symbol,
                "company_name": info.get("longName", "N/A"),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "market_cap": info.get("marketCap"),
                "revenue": info.get("totalRevenue"),
                "net_income": info.get("netIncomeToCommon"),
                "pe_ratio": info.get("trailingPE"),
                "pb_ratio": info.get("priceToBook"),
                "ps_ratio": info.get("priceToSalesTrailing12Months"),
                "roe": info.get("returnOnEquity"),
                "roa": info.get("returnOnAssets"),
                "profit_margin": info.get("profitMargins"),
                "operating_margin": info.get("operatingMargins"),
                "debt_to_equity": info.get("debtToEquity"),
                "current_ratio": info.get("currentRatio"),
                "quick_ratio": info.get("quickRatio"),
                "dividend_yield": info.get("dividendYield"),
                "beta": info.get("beta"),
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "target_price": info.get("targetMeanPrice"),
            }

            logger.info("Retrieved fundamentals", symbol=symbol)
            return fundamentals

        except Exception as e:
            logger.error("Failed to get fundamentals", symbol=symbol, error=str(e))
            return {"symbol": symbol, "error": str(e)}

    def get_financial_statements(self, symbol: str) -> dict[str, pd.DataFrame]:
        """
        Get financial statements for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with financial statements
        """
        try:
            ticker = yf.Ticker(symbol)

            statements = {
                "income_statement": ticker.financials,
                "balance_sheet": ticker.balance_sheet,
                "cash_flow": ticker.cashflow,
                "quarterly_income_statement": ticker.quarterly_financials,
                "quarterly_balance_sheet": ticker.quarterly_balance_sheet,
                "quarterly_cash_flow": ticker.quarterly_cashflow,
            }

            logger.info("Retrieved financial statements", symbol=symbol)
            return statements

        except Exception as e:
            logger.error("Failed to get financial statements", symbol=symbol, error=str(e))
            return {
                "income_statement": pd.DataFrame(),
                "balance_sheet": pd.DataFrame(),
                "cash_flow": pd.DataFrame(),
                "quarterly_income_statement": pd.DataFrame(),
                "quarterly_balance_sheet": pd.DataFrame(),
                "quarterly_cash_flow": pd.DataFrame(),
            }

    def get_options_chain(self, symbol: str, expiry_date: Optional[str] = None) -> dict[str, Any]:
        """
        Get options chain for a symbol.

        Args:
            symbol: Stock symbol
            expiry_date: Specific expiry date (optional)

        Returns:
            Dictionary with calls and puts DataFrames
        """
        try:
            ticker = yf.Ticker(symbol)

            # Get expiry date
            if expiry_date is None:
                expiries = ticker.options
                if not expiries:
                    return {"calls": pd.DataFrame(), "puts": pd.DataFrame()}
                expiry_date = expiries[0]

            # Get options chain
            options = ticker.option_chain(expiry_date)

            result = {
                "calls": options.calls,
                "puts": options.puts,
                "expiry": expiry_date,
            }

            logger.info(
                "Retrieved options chain",
                symbol=symbol,
                expiry=expiry_date,
                calls=len(options.calls),
                puts=len(options.puts),
            )
            return result

        except Exception as e:
            logger.error("Failed to get options chain", symbol=symbol, error=str(e))
            return {"calls": pd.DataFrame(), "puts": pd.DataFrame()}

    def get_available_expiries(self, symbol: str) -> list[str]:
        """
        Get available expiry dates for options.

        Args:
            symbol: Stock symbol

        Returns:
            List of expiry dates
        """
        try:
            ticker = yf.Ticker(symbol)
            expiries = list(ticker.options)
            logger.info("Retrieved expiry dates", symbol=symbol, count=len(expiries))
            return expiries
        except Exception as e:
            logger.error("Failed to get expiries", symbol=symbol, error=str(e))
            return []

    def calculate_technical_indicators(self, symbol: str) -> dict[str, Any]:
        """
        Calculate technical indicators for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with technical indicators
        """
        try:
            # Get price history
            history = self.get_price_history(symbol, period="1y", interval="1d")

            if history.empty or len(history) < 50:
                logger.warning("Insufficient data for indicators", symbol=symbol, rows=len(history))
                return {
                    "sma_20": None,
                    "sma_50": None,
                    "sma_200": None,
                    "ema_12": None,
                    "ema_26": None,
                    "rsi": None,
                    "macd": None,
                    "macd_signal": None,
                    "macd_histogram": None,
                    "bb_upper": None,
                    "bb_middle": None,
                    "bb_lower": None,
                    "current_price": history["Close"].iloc[-1] if len(history) > 0 else None,
                }

            close = history["Close"]
            high = history["High"]
            low = history["Low"]

            # Simple Moving Averages
            sma_20 = close.rolling(window=20).mean().iloc[-1] if len(close) >= 20 else None
            sma_50 = close.rolling(window=50).mean().iloc[-1] if len(close) >= 50 else None
            sma_200 = close.rolling(window=200).mean().iloc[-1] if len(close) >= 200 else None

            # Exponential Moving Averages
            ema_12 = close.ewm(span=12, adjust=False).mean().iloc[-1] if len(close) >= 12 else None
            ema_26 = close.ewm(span=26, adjust=False).mean().iloc[-1] if len(close) >= 26 else None

            # RSI
            rsi = self._calculate_rsi(close) if len(close) >= 14 else None

            # MACD
            macd_line = None
            signal_line = None
            histogram = None
            if ema_12 is not None and ema_26 is not None:
                macd_series = (
                    close.ewm(span=12, adjust=False).mean()
                    - close.ewm(span=26, adjust=False).mean()
                )
                macd_line = macd_series.iloc[-1]
                signal_series = macd_series.ewm(span=9, adjust=False).mean()
                signal_line = signal_series.iloc[-1]
                histogram = macd_line - signal_line

            # Bollinger Bands
            bb_middle = sma_20
            bb_std = close.rolling(window=20).std().iloc[-1] if len(close) >= 20 else None
            bb_upper = bb_middle + (2 * bb_std) if bb_middle and bb_std else None
            bb_lower = bb_middle - (2 * bb_std) if bb_middle and bb_std else None

            # Support and Resistance (simplified)
            recent_lows = low.tail(50).nsmallest(3).tolist() if len(low) >= 50 else []
            recent_highs = high.tail(50).nlargest(3).tolist() if len(high) >= 50 else []

            indicators = {
                "sma_20": sma_20,
                "sma_50": sma_50,
                "sma_200": sma_200,
                "ema_12": ema_12,
                "ema_26": ema_26,
                "rsi": rsi,
                "macd": macd_line,
                "macd_signal": signal_line,
                "macd_histogram": histogram,
                "bb_upper": bb_upper,
                "bb_middle": bb_middle,
                "bb_lower": bb_lower,
                "current_price": close.iloc[-1],
                "support_levels": sorted(recent_lows),
                "resistance_levels": sorted(recent_highs, reverse=True),
            }

            logger.info("Calculated technical indicators", symbol=symbol)
            return indicators

        except Exception as e:
            logger.error("Failed to calculate indicators", symbol=symbol, error=str(e))
            return {}

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> Optional[float]:
        """
        Calculate RSI (Relative Strength Index).

        Args:
            prices: Price series
            period: RSI period

        Returns:
            RSI value (0-100) or None
        """
        if len(prices) < period + 1:
            return None

        # Calculate price changes
        delta = prices.diff()

        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)

        # Calculate average gains and losses
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()

        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))

        return rsi.iloc[-1]

    def get_market_overview(self) -> dict[str, Any]:
        """
        Get overview of major market indices.

        Returns:
            Dictionary with market index data
        """
        try:
            indices = {
                "^GSPC": "S&P 500",
                "^DJI": "Dow Jones",
                "^IXIC": "NASDAQ",
                "^VIX": "VIX",
            }

            overview = {}
            for symbol, name in indices.items():
                try:
                    ticker = yf.Ticker(symbol)
                    history = ticker.history(period="5d")

                    if not history.empty:
                        current = history["Close"].iloc[-1]
                        previous = history["Close"].iloc[-2] if len(history) > 1 else current
                        change = ((current - previous) / previous) * 100

                        overview[name] = {
                            "symbol": symbol,
                            "price": current,
                            "change_pct": change,
                        }
                except Exception:
                    continue

            logger.info("Retrieved market overview", indices=len(overview))
            return overview

        except Exception as e:
            logger.error("Failed to get market overview", error=str(e))
            return {}
