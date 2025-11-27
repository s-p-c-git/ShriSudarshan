"""Market Intelligence Team - Janus-Pro Visual Analyst.

This module implements the "Visual Cortex" of the Deep Reasoner v2.0 architecture.
It uses Janus-Pro-7B for visual chart pattern recognition from candlestick images.

Note:
    Janus-Pro runs in an isolated Docker container exposing a REST API
    due to dependency conflicts with custom PyTorch requirements.
"""

import base64
import json
from io import BytesIO
from pathlib import Path
from typing import Any, Optional

import aiohttp

from ...config import settings
from ...config.prompts import JANUS_VISUAL_ANALYST_PROMPT
from ...data.schemas import (
    AgentRole,
    JanusVisualReport,
)
from ...utils import get_logger
from ..base import BaseAgent


logger = get_logger(__name__)

# Minimum price threshold to avoid division by zero issues
MIN_PRICE_THRESHOLD = 1e-6


class JanusVisualAnalyst(BaseAgent):
    """
    Janus-Pro Visual Analyst (Visual Cortex).

    Uses Janus-Pro-7B with decoupled visual encoding to analyze
    candlestick chart images and identify visual patterns.

    Key Features:
        - Raw chart image ingestion (not just OHLCV numbers)
        - Non-linear pattern recognition (Head & Shoulders, Wyckoff, etc.)
        - SigLIP-L encoder for chart reading
        - Runs in isolated Docker container via REST API

    Latency Profile:
        - Inference: ~2-5s (Medium Loop)
        - Suitable for periodic chart analysis
    """

    def __init__(self):
        """Initialize Janus Visual Analyst."""
        super().__init__(
            role=AgentRole.JANUS_VISUAL_ANALYST,
            system_prompt=JANUS_VISUAL_ANALYST_PROMPT,
            temperature=0.4,
        )
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def analyze(self, context: dict[str, Any]) -> JanusVisualReport:
        """
        Analyze a chart image for visual patterns.

        Args:
            context: Contains 'symbol', 'chart_image' (path or base64),
                    or 'chart_data' for generating chart

        Returns:
            JanusVisualReport with pattern analysis
        """
        symbol = context.get("symbol", "UNKNOWN")

        logger.info("Starting Janus visual analysis", symbol=symbol)

        try:
            # Get or generate chart image
            chart_image = await self._get_chart_image(context)

            if not chart_image:
                return JanusVisualReport(
                    symbol=symbol,
                    summary="No chart image available for analysis",
                    confidence=0.0,
                )

            # Check if Janus-Pro service is enabled
            if settings.janus_pro_enabled:
                report = await self._analyze_with_janus(symbol, chart_image)
            else:
                # Fallback to LLM-based analysis with description
                report = await self._analyze_with_llm_fallback(symbol, context)

            logger.info(
                "Visual analysis complete",
                symbol=symbol,
                patterns_found=len(report.patterns_detected),
            )

            return report

        except Exception as e:
            logger.error("Visual analysis failed", symbol=symbol, error=str(e))
            return JanusVisualReport(
                symbol=symbol,
                summary=f"Analysis failed: {str(e)}",
                confidence=0.1,
            )

    async def _get_chart_image(self, context: dict[str, Any]) -> Optional[str]:
        """
        Get chart image from context or generate one.

        Args:
            context: May contain 'chart_image', 'chart_path', or 'chart_data'

        Returns:
            Base64 encoded image string or None
        """
        # Check for direct image input
        if "chart_image" in context:
            return context["chart_image"]

        # Check for file path
        if "chart_path" in context:
            chart_path = Path(context["chart_path"])
            if chart_path.exists():
                with open(chart_path, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")

        # Generate chart from price data if available
        if "chart_data" in context or "price_history" in context:
            return await self._generate_chart_image(context)

        return None

    async def _generate_chart_image(self, context: dict[str, Any]) -> Optional[str]:
        """
        Generate a candlestick chart image from price data.

        Uses mplfinance for chart generation.

        Args:
            context: Contains 'chart_data' or 'price_history' DataFrame

        Returns:
            Base64 encoded PNG image
        """
        try:
            import mplfinance as mpf

            df = context.get("chart_data") or context.get("price_history")

            if df is None or df.empty:
                return None

            # Ensure proper column names
            df = df.copy()
            df.columns = [c.title() for c in df.columns]

            # Validate required OHLCV columns
            required_cols = {"Open", "High", "Low", "Close"}
            missing_cols = required_cols - set(df.columns)
            if missing_cols:
                logger.warning(
                    "Chart data missing required columns",
                    missing=list(missing_cols),
                    available=list(df.columns),
                )
                return None

            # Generate candlestick chart
            buf = BytesIO()
            # Only include volume if Volume column exists
            has_volume = "Volume" in df.columns
            mpf.plot(
                df.tail(60),  # Last 60 periods
                type="candle",
                style="charles",
                volume=has_volume,
                mav=(10, 20, 50),
                savefig={"fname": buf, "format": "png", "dpi": 150},
                figsize=(12, 8),
            )
            buf.seek(0)

            return base64.b64encode(buf.read()).decode("utf-8")

        except ImportError:
            logger.warning("mplfinance not installed, cannot generate charts")
            return None
        except Exception as e:
            logger.warning("Failed to generate chart", error=str(e))
            return None

    async def _analyze_with_janus(
        self, symbol: str, chart_image: str
    ) -> JanusVisualReport:
        """
        Analyze chart using Janus-Pro REST API.

        Args:
            symbol: Stock symbol
            chart_image: Base64 encoded image

        Returns:
            JanusVisualReport from Janus-Pro
        """
        session = await self._get_session()

        payload = {
            "image": chart_image,
            "prompt": f"""Analyze this {symbol} candlestick chart for visual patterns.

Identify:
1. Chart patterns (Head & Shoulders, Double Top/Bottom, Triangles, etc.)
2. Trend lines and channels
3. Support/Resistance zones
4. Candlestick patterns
5. Volume patterns

Provide structured JSON output with pattern details and confidence scores.
""",
        }

        try:
            endpoint = f"{settings.janus_pro_endpoint}/analyze"
            async with session.post(
                endpoint,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return self._parse_janus_response(symbol, result, chart_image)
                else:
                    error = await response.text()
                    logger.warning(
                        "Janus-Pro API error",
                        status=response.status,
                        error=error,
                    )
                    return await self._analyze_with_llm_fallback(
                        symbol, {"chart_image": chart_image}
                    )

        except aiohttp.ClientError as e:
            logger.warning("Janus-Pro connection failed", error=str(e))
            return await self._analyze_with_llm_fallback(
                symbol, {"chart_image": chart_image}
            )

    def _parse_janus_response(
        self, symbol: str, result: dict, chart_image: str
    ) -> JanusVisualReport:
        """Parse Janus-Pro API response into a report."""
        patterns = result.get("patterns", [])
        confidence = result.get("confidence", 0.5)

        # Structure patterns
        structured_patterns = []
        for p in patterns:
            structured_patterns.append({
                "name": p.get("name", "Unknown"),
                "confidence": p.get("confidence", 0.5),
                "location": p.get("location", ""),
                "stage": p.get("stage", "forming"),
                "target": p.get("price_target"),
                "invalidation": p.get("invalidation_level"),
            })

        return JanusVisualReport(
            symbol=symbol,
            summary=result.get("summary", "Visual analysis complete"),
            confidence=confidence,
            patterns_detected=structured_patterns,
            chart_description=result.get("description", ""),
            trend_analysis=result.get("trend", ""),
            support_resistance_visual=result.get("levels", {}),
            pattern_confluence=result.get("confluence", []),
            trading_implications=result.get("implications", ""),
            image_analyzed=chart_image[:100] + "...",  # Truncate for logging
        )

    async def _analyze_with_llm_fallback(
        self, symbol: str, context: dict[str, Any]
    ) -> JanusVisualReport:
        """
        Fallback to LLM-based analysis when Janus-Pro is unavailable.

        This uses textual description of the chart rather than visual analysis.

        Args:
            symbol: Stock symbol
            context: Context with technical data

        Returns:
            JanusVisualReport from LLM analysis
        """
        logger.info("Using LLM fallback for visual analysis", symbol=symbol)

        # Build prompt from available data
        technical_data = context.get("technical_indicators", {})
        price_data = context.get("chart_data") or context.get("price_history")

        if price_data is not None and not price_data.empty:
            recent = price_data.tail(20)
            current_close = recent["Close"].iloc[-1]
            high_max = recent["High"].max()
            low_min = recent["Low"].min()

            # Explicitly handle zero or near-zero close price
            if current_close is None or abs(current_close) < MIN_PRICE_THRESHOLD:
                logger.warning(
                    "Invalid or zero current_close in price data for LLM fallback",
                    symbol=symbol,
                    current_close=current_close,
                )
                price_summary = (
                    "Recent price data is invalid (current price is zero or missing)."
                )
            else:
                range_pct = ((high_max - low_min) / current_close * 100)
                price_summary = f"""
Recent price action (last 20 periods):
- High: ${high_max:.2f}
- Low: ${low_min:.2f}
- Current: ${current_close:.2f}
- Range: {range_pct:.1f}%
"""
        else:
            price_summary = "No recent price data available."

        prompt = f"""
Based on the following market data for {symbol}, identify potential chart patterns
that would be visible if analyzing a candlestick chart:

{price_summary}

Technical Indicators:
{json.dumps(technical_data, indent=2) if technical_data else "Not available"}

Identify patterns and provide analysis in JSON format:
{{
    "patterns_detected": [
        {{"name": "pattern_name", "confidence": 0.0-1.0, "stage": "forming/complete"}}
    ],
    "trend_analysis": "description",
    "support_resistance": {{"support": [], "resistance": []}},
    "trading_implications": "implications",
    "confidence_score": 0.0-1.0,
    "summary": "brief summary"
}}
"""

        response = await self._generate_response(prompt)

        try:
            # Parse JSON response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            parsed = json.loads(json_str)

            return JanusVisualReport(
                symbol=symbol,
                summary=parsed.get("summary", "LLM-based pattern analysis"),
                confidence=parsed.get("confidence_score", 0.5),
                patterns_detected=parsed.get("patterns_detected", []),
                trend_analysis=parsed.get("trend_analysis", ""),
                support_resistance_visual=parsed.get("support_resistance", {}),
                trading_implications=parsed.get("trading_implications", ""),
            )

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Failed to parse LLM fallback response", error=str(e))
            return JanusVisualReport(
                symbol=symbol,
                summary=response[:500],
                confidence=0.3,
            )
