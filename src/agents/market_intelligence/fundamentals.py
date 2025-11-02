"""Market Intelligence Team - Fundamentals Analyst."""

import json
from typing import Any, Dict

from ..base import BaseAgent
from ...config.prompts import FUNDAMENTALS_ANALYST_PROMPT
from ...data.schemas import AgentRole, FundamentalsReport, Sentiment
from ...data.providers import MarketDataProvider
from ...utils import get_logger

logger = get_logger(__name__)


class FundamentalsAnalyst(BaseAgent):
    """
    Fundamentals Analyst agent.
    
    Analyzes financial reports, earnings transcripts, and balance sheets
    to determine intrinsic value of assets.
    """
    
    def __init__(self):
        super().__init__(
            role=AgentRole.FUNDAMENTALS_ANALYST,
            system_prompt=FUNDAMENTALS_ANALYST_PROMPT,
            temperature=0.5,  # Lower temperature for factual analysis
        )
        self.data_provider = MarketDataProvider()
    
    async def analyze(self, context: Dict[str, Any]) -> FundamentalsReport:
        """
        Analyze fundamental data for a symbol.
        
        Args:
            context: Contains 'symbol', 'market_data_provider' (optional)
            
        Returns:
            FundamentalsReport with analysis
        """
        symbol = context.get("symbol", "UNKNOWN")
        
        # Use provided data provider or default
        data_provider = context.get("market_data_provider", self.data_provider)
        
        logger.info("Starting fundamental analysis", symbol=symbol)
        
        try:
            # Fetch fundamental data
            fundamentals = data_provider.get_fundamentals(symbol)
            info = data_provider.get_info(symbol)
            
            # Get current price for valuation
            current_price = data_provider.get_current_price(symbol)
            
            # Construct detailed input for LLM
            input_text = f"""
Analyze the fundamental data for {symbol} and provide a comprehensive investment analysis.

COMPANY INFORMATION:
- Name: {info.get('longName', 'N/A')}
- Sector: {fundamentals.get('sector', 'N/A')}
- Industry: {fundamentals.get('industry', 'N/A')}
- Current Price: ${current_price or 'N/A'}

VALUATION METRICS:
- Market Cap: ${fundamentals.get('market_cap', 'N/A')}
- Enterprise Value: ${fundamentals.get('enterprise_value', 'N/A')}
- P/E Ratio (Trailing): {fundamentals.get('trailing_pe', 'N/A')}
- P/E Ratio (Forward): {fundamentals.get('forward_pe', 'N/A')}
- PEG Ratio: {fundamentals.get('peg_ratio', 'N/A')}
- Price to Book: {fundamentals.get('price_to_book', 'N/A')}
- Price to Sales: {fundamentals.get('price_to_sales', 'N/A')}

PROFITABILITY:
- Profit Margin: {fundamentals.get('profit_margins', 'N/A')}
- Operating Margin: {fundamentals.get('operating_margins', 'N/A')}
- Return on Equity: {fundamentals.get('return_on_equity', 'N/A')}
- Return on Assets: {fundamentals.get('return_on_assets', 'N/A')}

GROWTH:
- Revenue Growth: {fundamentals.get('revenue_growth', 'N/A')}
- Earnings Growth: {fundamentals.get('earnings_growth', 'N/A')}

FINANCIAL HEALTH:
- Debt to Equity: {fundamentals.get('debt_to_equity', 'N/A')}
- Current Ratio: {fundamentals.get('current_ratio', 'N/A')}
- Quick Ratio: {fundamentals.get('quick_ratio', 'N/A')}
- Free Cash Flow: ${fundamentals.get('free_cash_flow', 'N/A')}

DIVIDEND:
- Dividend Yield: {fundamentals.get('dividend_yield', 'N/A')}
- Payout Ratio: {fundamentals.get('payout_ratio', 'N/A')}

TECHNICAL FACTORS:
- Beta: {fundamentals.get('beta', 'N/A')}
- 52 Week High: ${fundamentals.get('52_week_high', 'N/A')}
- 52 Week Low: ${fundamentals.get('52_week_low', 'N/A')}

Please provide your analysis in the following JSON format:
{{
    "key_points": ["point1", "point2", "point3"],
    "intrinsic_value_estimate": <number or null>,
    "investment_thesis": "bullish" or "bearish" or "neutral",
    "risk_factors": ["risk1", "risk2", "risk3"],
    "confidence_level": <1-10>,
    "analysis_summary": "brief summary of your analysis"
}}
"""
            
            # Generate analysis
            response = await self._generate_response(input_text)
            
            # Try to parse JSON response
            try:
                # Extract JSON from response (handle markdown code blocks)
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0].strip()
                else:
                    json_str = response.strip()
                
                parsed = json.loads(json_str)
                
                # Extract fields with defaults
                key_points = parsed.get("key_points", [])
                intrinsic_value = parsed.get("intrinsic_value_estimate")
                investment_thesis_str = parsed.get("investment_thesis", "neutral").lower()
                risk_factors = parsed.get("risk_factors", [])
                confidence_level = parsed.get("confidence_level", 5)
                analysis_summary = parsed.get("analysis_summary", response[:500])
                
                # Map investment thesis to Sentiment enum
                if investment_thesis_str in ["bullish", "buy", "positive"]:
                    investment_thesis = Sentiment.BULLISH
                elif investment_thesis_str in ["bearish", "sell", "negative"]:
                    investment_thesis = Sentiment.BEARISH
                else:
                    investment_thesis = Sentiment.NEUTRAL
                
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                logger.warning("Failed to parse LLM response as JSON, using defaults", error=str(e))
                key_points = ["Analysis pending - parsing error"]
                intrinsic_value = None
                investment_thesis = Sentiment.NEUTRAL
                risk_factors = ["Unable to parse detailed analysis"]
                confidence_level = 5
                analysis_summary = response[:500]
            
            report = FundamentalsReport(
                symbol=symbol,
                confidence_level=confidence_level,
                analysis=analysis_summary,
                key_points=key_points,
                intrinsic_value=intrinsic_value,
                financial_metrics=fundamentals,
                investment_thesis=investment_thesis,
                risk_factors=risk_factors,
            )
            
            logger.info(
                "Fundamental analysis complete",
                symbol=symbol,
                thesis=investment_thesis.value,
                confidence=confidence_level,
            )
            
            return report
            
        except Exception as e:
            logger.error("Fundamental analysis failed", symbol=symbol, error=str(e))
            
            # Return error report
            return FundamentalsReport(
                symbol=symbol,
                confidence_level=1,
                analysis=f"Analysis failed: {str(e)}",
                key_points=["Analysis error occurred"],
                intrinsic_value=None,
                financial_metrics={},
                investment_thesis=Sentiment.NEUTRAL,
                risk_factors=[f"Error: {str(e)}"],
            )
