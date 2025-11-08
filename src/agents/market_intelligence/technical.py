"""Market Intelligence Team - Technical Analyst."""

import json
from typing import Any

import pandas as pd

from ...config.prompts import TECHNICAL_ANALYST_PROMPT
from ...data.providers import MarketDataProvider
from ...data.schemas import AgentRole, TechnicalReport, TrendDirection
from ...utils import get_logger
from ..base import BaseAgent


logger = get_logger(__name__)


class TechnicalAnalyst(BaseAgent):
    """
    Technical Analyst agent.

    Analyzes price charts, volume data, and technical indicators to identify
    patterns, trends, and key support/resistance levels.
    """

    def __init__(self):
        super().__init__(
            role=AgentRole.TECHNICAL_ANALYST,
            system_prompt=TECHNICAL_ANALYST_PROMPT,
            temperature=0.5,
        )
        self.market_data_provider = MarketDataProvider()

    def _identify_support_resistance(
        self, df: pd.DataFrame, window: int = 20
    ) -> tuple[list[float], list[float]]:
        """
        Identify support and resistance levels using local minima/maxima.

        Args:
            df: DataFrame with price data
            window: Window for local min/max detection

        Returns:
            Tuple of (support_levels, resistance_levels)
        """
        if df.empty or len(df) < window * 2:
            return [], []

        highs = df["High"].values
        lows = df["Low"].values

        # Find local maxima (resistance)
        resistance = []
        for i in range(window, len(highs) - window):
            if highs[i] == max(highs[i - window : i + window + 1]):
                resistance.append(float(highs[i]))

        # Find local minima (support)
        support = []
        for i in range(window, len(lows) - window):
            if lows[i] == min(lows[i - window : i + window + 1]):
                support.append(float(lows[i]))

        # Cluster nearby levels (within 2%)
        def cluster_levels(levels: list[float], tolerance: float = 0.02) -> list[float]:
            if not levels:
                return []

            levels = sorted(levels)
            clustered = []
            current_cluster = [levels[0]]

            for level in levels[1:]:
                if abs(level - current_cluster[-1]) / current_cluster[-1] < tolerance:
                    current_cluster.append(level)
                else:
                    clustered.append(sum(current_cluster) / len(current_cluster))
                    current_cluster = [level]

            clustered.append(sum(current_cluster) / len(current_cluster))
            return clustered

        support_levels = cluster_levels(support)[-5:]  # Top 5 support levels
        resistance_levels = cluster_levels(resistance)[-5:]  # Top 5 resistance levels

        return support_levels, resistance_levels

    def _detect_chart_patterns(self, df: pd.DataFrame) -> list[str]:
        """
        Detect basic chart patterns.

        Args:
            df: DataFrame with price and indicator data

        Returns:
            List of detected patterns
        """
        patterns = []

        if df.empty or len(df) < 50:
            return patterns

        try:
            # Get recent data
            recent = df.tail(50)
            close = recent["Close"]

            # Moving average crossovers
            if "SMA_20" in recent.columns and "SMA_50" in recent.columns:
                sma20 = recent["SMA_20"]
                sma50 = recent["SMA_50"]

                # Golden cross
                if sma20.iloc[-2] < sma50.iloc[-2] and sma20.iloc[-1] > sma50.iloc[-1]:
                    patterns.append("Golden Cross (SMA 20/50)")

                # Death cross
                if sma20.iloc[-2] > sma50.iloc[-2] and sma20.iloc[-1] < sma50.iloc[-1]:
                    patterns.append("Death Cross (SMA 20/50)")

            # MACD crossover
            if "MACD" in recent.columns and "MACD_Signal" in recent.columns:
                macd = recent["MACD"]
                signal = recent["MACD_Signal"]

                if macd.iloc[-2] < signal.iloc[-2] and macd.iloc[-1] > signal.iloc[-1]:
                    patterns.append("MACD Bullish Crossover")

                if macd.iloc[-2] > signal.iloc[-2] and macd.iloc[-1] < signal.iloc[-1]:
                    patterns.append("MACD Bearish Crossover")

            # RSI levels
            if "RSI" in recent.columns:
                rsi = recent["RSI"].iloc[-1]
                if rsi > 70:
                    patterns.append("RSI Overbought (>70)")
                elif rsi < 30:
                    patterns.append("RSI Oversold (<30)")

            # Bollinger Bands
            if all(col in recent.columns for col in ["BB_Upper", "BB_Lower", "Close"]):
                close_val = close.iloc[-1]
                bb_upper = recent["BB_Upper"].iloc[-1]
                bb_lower = recent["BB_Lower"].iloc[-1]

                if close_val > bb_upper:
                    patterns.append("Price Above Upper Bollinger Band")
                elif close_val < bb_lower:
                    patterns.append("Price Below Lower Bollinger Band")

            # Price trend
            if len(close) >= 20:
                recent_change = (close.iloc[-1] - close.iloc[-20]) / close.iloc[-20] * 100
                if recent_change > 10:
                    patterns.append(f"Strong Uptrend (+{recent_change:.1f}% in 20 days)")
                elif recent_change < -10:
                    patterns.append(f"Strong Downtrend ({recent_change:.1f}% in 20 days)")

        except Exception as e:
            logger.warning("Error detecting patterns", error=str(e))

        return patterns

    async def analyze(self, context: dict[str, Any]) -> TechnicalReport:
        """
        Analyze technical data for a symbol.

        Args:
            context: Contains 'symbol', optional providers

        Returns:
            TechnicalReport with analysis
        """
        symbol = context.get("symbol", "UNKNOWN")

        # Use provided provider or default
        data_provider = context.get("market_data_provider", self.market_data_provider)

        logger.info("Starting technical analysis", symbol=symbol)

        try:
            # Fetch price data
            price_data = data_provider.get_price_history(symbol, period="6mo", interval="1d")

            if price_data.empty:
                raise ValueError("No price data available")

            # Calculate technical indicators
            price_data = data_provider.calculate_technical_indicators(price_data)

            # Identify support and resistance
            support_levels, resistance_levels = self._identify_support_resistance(price_data)

            # Detect chart patterns
            chart_patterns = self._detect_chart_patterns(price_data)

            # Get current price and indicators
            current_price = float(price_data["Close"].iloc[-1])
            current_rsi = float(price_data["RSI"].iloc[-1]) if "RSI" in price_data.columns else None
            current_macd = (
                float(price_data["MACD"].iloc[-1]) if "MACD" in price_data.columns else None
            )

            # Determine trend
            if "SMA_50" in price_data.columns and "SMA_200" in price_data.columns:
                sma50 = price_data["SMA_50"].iloc[-1]
                sma200 = price_data["SMA_200"].iloc[-1]

                if current_price > sma50 > sma200:
                    trend_direction = TrendDirection.UPTREND
                    trend_desc = "uptrend"
                elif current_price < sma50 < sma200:
                    trend_direction = TrendDirection.DOWNTREND
                    trend_desc = "downtrend"
                else:
                    trend_direction = TrendDirection.SIDEWAYS
                    trend_desc = "sideways"
            else:
                # Fallback to simple price momentum
                price_change = (
                    price_data["Close"].iloc[-1] - price_data["Close"].iloc[-20]
                ) / price_data["Close"].iloc[-20]
                if price_change > 0.05:
                    trend_direction = TrendDirection.UPTREND
                    trend_desc = "uptrend"
                elif price_change < -0.05:
                    trend_direction = TrendDirection.DOWNTREND
                    trend_desc = "downtrend"
                else:
                    trend_direction = TrendDirection.SIDEWAYS
                    trend_desc = "sideways"

            # Prepare indicators for LLM
            indicators_text = f"""
- Current Price: ${current_price:.2f}
- RSI (14): {current_rsi:.2f if current_rsi else 'N/A'}
- MACD: {current_macd:.4f if current_macd else 'N/A'}
- 20-day SMA: ${price_data["SMA_20"].iloc[-1]:.2f if 'SMA_20' in price_data.columns else 'N/A'}
- 50-day SMA: ${price_data["SMA_50"].iloc[-1]:.2f if 'SMA_50' in price_data.columns else 'N/A'}
- 200-day SMA: ${price_data["SMA_200"].iloc[-1]:.2f if 'SMA_200' in price_data.columns else 'N/A'}
- ATR: ${price_data["ATR"].iloc[-1]:.2f if 'ATR' in price_data.columns else 'N/A'}
"""

            # Construct input for LLM
            input_text = f"""
Analyze the technical indicators and price action for {symbol}.

TREND ANALYSIS:
- Current Trend: {trend_desc}
- Price: ${current_price:.2f}

TECHNICAL INDICATORS:
{indicators_text}

SUPPORT LEVELS:
{", ".join([f"${level:.2f}" for level in support_levels]) if support_levels else "None identified"}

RESISTANCE LEVELS:
{", ".join([f"${level:.2f}" for level in resistance_levels]) if resistance_levels else "None identified"}

DETECTED PATTERNS:
{chr(10).join([f"- {pattern}" for pattern in chart_patterns]) if chart_patterns else "- No significant patterns detected"}

Please provide your technical analysis in JSON format:
{{
    "trend_direction": "bullish" or "bearish" or "neutral",
    "key_points": ["point1", "point2", "point3"],
    "chart_patterns_interpretation": ["interpretation1", "interpretation2"],
    "confidence_level": <1-10>,
    "analysis_summary": "brief summary"
}}
"""

            # Generate analysis
            response = await self._generate_response(input_text)

            # Parse JSON response
            try:
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0].strip()
                else:
                    json_str = response.strip()

                parsed = json.loads(json_str)

                trend_str = parsed.get("trend_direction", trend_desc).lower()
                key_points = parsed.get("key_points", [])
                pattern_interp = parsed.get("chart_patterns_interpretation", chart_patterns)
                confidence_level = parsed.get("confidence_level", 6)
                analysis_summary = parsed.get("analysis_summary", response[:500])

                # Map trend
                if trend_str in ["bullish", "uptrend", "up"]:
                    final_trend = TrendDirection.UPTREND
                elif trend_str in ["bearish", "downtrend", "down"]:
                    final_trend = TrendDirection.DOWNTREND
                else:
                    final_trend = TrendDirection.SIDEWAYS

            except (json.JSONDecodeError, KeyError, IndexError) as e:
                logger.warning("Failed to parse LLM response, using defaults", error=str(e))
                final_trend = trend_direction
                pattern_interp = chart_patterns
                confidence_level = 6
                analysis_summary = response[:500]

            # Prepare indicators dict
            indicators_dict = {
                "current_price": current_price,
                "rsi": current_rsi,
                "macd": current_macd,
                "sma_20": (
                    float(price_data["SMA_20"].iloc[-1]) if "SMA_20" in price_data.columns else None
                ),
                "sma_50": (
                    float(price_data["SMA_50"].iloc[-1]) if "SMA_50" in price_data.columns else None
                ),
                "sma_200": (
                    float(price_data["SMA_200"].iloc[-1])
                    if "SMA_200" in price_data.columns
                    else None
                ),
                "atr": (float(price_data["ATR"].iloc[-1]) if "ATR" in price_data.columns else None),
            }

            report = TechnicalReport(
                symbol=symbol,
                confidence=confidence_level / 10.0,  # Convert 1-10 to 0.0-1.0
                summary=analysis_summary,
                trend_direction=final_trend,
                support_levels=support_levels,
                resistance_levels=resistance_levels,
                indicators=indicators_dict,
                chart_patterns=pattern_interp,
            )

            logger.info(
                "Technical analysis complete",
                symbol=symbol,
                trend=final_trend.value,
                confidence=confidence_level,
            )

            return report

        except Exception as e:
            logger.error("Technical analysis failed", symbol=symbol, error=str(e))

            return TechnicalReport(
                symbol=symbol,
                confidence=0.1,  # Low confidence on error
                summary=f"Analysis failed: {str(e)}",
                trend_direction=TrendDirection.SIDEWAYS,
                support_levels=[],
                resistance_levels=[],
                indicators={},
                chart_patterns=[],
            )
