"""
Advanced example: Custom agent integration and workflow customization.

This example demonstrates:
1. Creating a custom agent
2. Integrating it into the workflow
3. Using custom decision logic
4. Implementing custom risk parameters
"""

import asyncio
from typing import Any

from src.agents.base import BaseAgent
from src.data.providers import MarketDataProvider
from src.data.schemas import AgentReport, AgentRole
from src.orchestration import TradingWorkflow
from src.utils import get_logger


logger = get_logger(__name__)


# Custom Agent Example
class CustomVolatilityAnalyst(BaseAgent):
    """
    Custom agent that analyzes volatility patterns.

    This agent could be added to the Market Intelligence team
    to provide additional volatility insights.
    """

    def __init__(self):
        # Define custom system prompt
        system_prompt = """You are a Volatility Analyst for Project Shri Sudarshan.

        Your role is to analyze historical volatility patterns and predict future volatility.

        Focus on:
        - Historical volatility trends (30, 60, 90 day)
        - Implied volatility vs historical volatility gaps
        - Volatility regime identification (low, medium, high)
        - Mean reversion patterns
        - Volatility term structure

        Provide structured analysis with:
        1. Current volatility regime
        2. Expected volatility direction (increasing/decreasing/stable)
        3. Volatility-adjusted strategy recommendations
        4. Key volatility levels to watch
        5. Confidence level (1-10)
        """

        # Initialize with custom role
        super().__init__(
            role=AgentRole.TECHNICAL_ANALYST,  # Reuse existing role or create new
            system_prompt=system_prompt,
            temperature=0.6,
        )

        self.data_provider = MarketDataProvider()

    async def analyze(self, context: dict[str, Any]) -> AgentReport:
        """
        Analyze volatility for a symbol.

        Args:
            context: Contains 'symbol', 'market_data_provider' (optional)

        Returns:
            AgentReport with volatility analysis
        """
        symbol = context.get("symbol", "UNKNOWN")
        data_provider = context.get("market_data_provider", self.data_provider)

        logger.info("Starting volatility analysis", symbol=symbol)

        try:
            # Get price history
            history = data_provider.get_price_history(symbol, period="6mo", interval="1d")

            if history.empty:
                raise ValueError("No price history available")

            # Calculate historical volatility
            returns = history["Close"].pct_change()
            hv_30 = returns.rolling(30).std() * (252**0.5)  # Annualized
            hv_60 = returns.rolling(60).std() * (252**0.5)
            hv_90 = returns.rolling(90).std() * (252**0.5)

            current_hv_30 = hv_30.iloc[-1] if not hv_30.empty else None
            current_hv_60 = hv_60.iloc[-1] if not hv_60.empty else None
            current_hv_90 = hv_90.iloc[-1] if not hv_90.empty else None

            # Get technical indicators for context
            indicators = data_provider.calculate_technical_indicators(symbol)

            # Construct analysis input
            input_text = f"""
Analyze the volatility pattern for {symbol}.

HISTORICAL VOLATILITY:
- 30-day HV: {current_hv_30:.2%} if current_hv_30 else 'N/A'
- 60-day HV: {current_hv_60:.2%} if current_hv_60 else 'N/A'
- 90-day HV: {current_hv_90:.2%} if current_hv_90 else 'N/A'

PRICE CONTEXT:
- Current Price: ${history['Close'].iloc[-1]:.2f}
- 52-week High/Low: ${history['Close'].max():.2f} / ${history['Close'].min():.2f}
- RSI: {indicators.get('rsi', 'N/A')}

Provide your volatility analysis and recommendations.
"""

            # Generate LLM response
            response = await self._generate_response(input_text)

            # Create report
            report = AgentReport(
                symbol=symbol,
                summary=response[:500],
                confidence=0.7,
                agent_role=self.role,
                metadata={
                    "hv_30": float(current_hv_30) if current_hv_30 else None,
                    "hv_60": float(current_hv_60) if current_hv_60 else None,
                    "hv_90": float(current_hv_90) if current_hv_90 else None,
                    "analysis": response,
                },
            )

            logger.info(
                "Volatility analysis complete",
                symbol=symbol,
                hv_30=f"{current_hv_30:.2%}" if current_hv_30 else "N/A",
            )

            return report

        except Exception as e:
            logger.error("Volatility analysis failed", symbol=symbol, error=str(e))

            # Return error report
            return AgentReport(
                symbol=symbol,
                summary=f"Analysis failed: {str(e)}",
                confidence=0.0,
                agent_role=self.role,
                metadata={"error": str(e)},
            )


# Custom Workflow Integration
class CustomTradingWorkflow(TradingWorkflow):
    """
    Extended trading workflow with custom agent integration.
    """

    def __init__(self):
        super().__init__()
        self.volatility_analyst = CustomVolatilityAnalyst()

    async def run_custom_analysis(self, symbol: str):
        """
        Run analysis with additional custom agent.

        Args:
            symbol: Stock ticker

        Returns:
            Dict with all analysis results
        """
        logger.info(f"Starting custom workflow for {symbol}")

        # Run standard analysis
        result = await self.run(symbol)

        # Add custom volatility analysis
        volatility_context = {"symbol": symbol}
        volatility_report = await self.volatility_analyst.analyze(volatility_context)

        result["volatility_analysis"] = volatility_report

        logger.info(f"Custom workflow complete for {symbol}")

        return result


# Custom Risk Parameters Example
def custom_risk_assessment(strategy_proposal, portfolio_state):
    """
    Custom risk assessment logic.

    This function demonstrates how to implement custom risk checks
    beyond the standard risk manager.
    """
    risks = []
    approved = True

    # Check 1: Maximum leverage
    if hasattr(strategy_proposal, "leverage"):
        if strategy_proposal.leverage > 2.0:
            risks.append("Leverage exceeds 2x limit")
            approved = False

    # Check 2: Options-specific risks
    if "option" in strategy_proposal.strategy_type.value.lower():
        # Check time to expiration
        if hasattr(strategy_proposal, "expiration_days"):
            if strategy_proposal.expiration_days < 7:
                risks.append("Options expiration too near (<7 days)")
                # Don't reject, just warn

    # Check 3: Portfolio diversification
    if portfolio_state:
        symbol = strategy_proposal.symbol
        existing_exposure = portfolio_state.get("positions", {}).get(symbol, 0)
        new_exposure = strategy_proposal.position_size
        total_exposure = existing_exposure + new_exposure

        if total_exposure > 0.10:  # 10% max single stock exposure
            risks.append(f"Total exposure to {symbol} would exceed 10%")
            approved = False

    # Check 4: Market conditions
    # Example: Don't trade during high VIX
    # vix = get_vix_level()  # Would need to implement
    # if vix > 30:
    #     risks.append("VIX above 30, elevated market risk")

    return {
        "approved": approved,
        "risks": risks,
        "recommendation": "Approved" if approved else "Rejected",
    }


# Advanced Usage Examples
async def example_custom_agent():
    """Example: Using custom volatility analyst."""
    agent = CustomVolatilityAnalyst()

    context = {"symbol": "AAPL"}
    report = await agent.analyze(context)

    print("\n" + "=" * 60)
    print("Custom Volatility Analysis")
    print("=" * 60)
    print(f"Symbol: {report.symbol}")
    print(f"Confidence: {report.confidence:.2f}")
    print("\nMetadata:")
    for key, value in report.metadata.items():
        if key != "analysis":  # Skip full analysis text
            print(f"  {key}: {value}")
    print("=" * 60 + "\n")


async def example_custom_workflow():
    """Example: Using custom workflow with additional analysis."""
    workflow = CustomTradingWorkflow()

    result = await workflow.run_custom_analysis("AAPL")

    print("\n" + "=" * 60)
    print("Custom Workflow Results")
    print("=" * 60)

    # Standard results
    print(f"Analysis Complete: {result.get('analysis_complete', False)}")
    print(f"Strategy Complete: {result.get('strategy_complete', False)}")

    # Custom volatility analysis
    if "volatility_analysis" in result:
        vol_report = result["volatility_analysis"]
        print("\nVolatility Analysis:")
        print(f"  Confidence: {vol_report.confidence:.2f}")
        print(f"  30-day HV: {vol_report.metadata.get('hv_30', 'N/A')}")
        print(f"  60-day HV: {vol_report.metadata.get('hv_60', 'N/A')}")

    print("=" * 60 + "\n")


async def example_portfolio_monitoring():
    """
    Example: Monitor portfolio with custom metrics.

    This demonstrates how to build custom portfolio monitoring
    on top of the existing system.
    """
    from src.memory import EpisodicMemory

    memory = EpisodicMemory()

    # Get all open trades
    all_trades = memory.get_all_trades()
    open_trades = [t for t in all_trades if t.outcome == "pending"]

    print("\n" + "=" * 60)
    print("Portfolio Monitor")
    print("=" * 60)

    # Calculate portfolio metrics
    total_exposure = 0
    positions_by_symbol = {}

    for trade in open_trades:
        # Calculate current value (simplified)
        position_value = trade.quantity * trade.entry_price
        total_exposure += position_value

        if trade.symbol not in positions_by_symbol:
            positions_by_symbol[trade.symbol] = []
        positions_by_symbol[trade.symbol].append(trade)

    print(f"\nTotal Open Positions: {len(open_trades)}")
    print(f"Total Exposure: ${total_exposure:,.2f}")
    print(f"Unique Symbols: {len(positions_by_symbol)}")

    # Show positions by symbol
    print("\nPositions by Symbol:")
    for symbol, trades in positions_by_symbol.items():
        symbol_exposure = sum(t.quantity * t.entry_price for t in trades)
        exposure_pct = (symbol_exposure / total_exposure) * 100 if total_exposure > 0 else 0
        print(f"  {symbol}: {len(trades)} positions, ${symbol_exposure:,.2f} ({exposure_pct:.1f}%)")

    # Calculate unrealized P&L (would need current prices)
    print("\nNote: For real-time P&L, integrate with MarketDataProvider.get_current_price()")

    print("=" * 60 + "\n")


async def example_risk_scenario_analysis():
    """
    Example: Scenario analysis for portfolio risk.

    Tests portfolio performance under various market scenarios.
    """
    from src.data.providers import MarketDataProvider

    provider = MarketDataProvider()
    symbols = ["AAPL", "GOOGL", "MSFT"]

    print("\n" + "=" * 60)
    print("Risk Scenario Analysis")
    print("=" * 60)

    scenarios = {
        "market_crash": -0.20,  # -20%
        "correction": -0.10,  # -10%
        "mild_decline": -0.05,  # -5%
        "stable": 0.00,  # 0%
        "mild_growth": 0.05,  # +5%
        "rally": 0.10,  # +10%
    }

    # Get current prices
    current_prices = {}
    for symbol in symbols:
        price = provider.get_current_price(symbol)
        if price:
            current_prices[symbol] = price

    if not current_prices:
        print("Unable to fetch current prices")
        return

    # Simulate portfolio (equal weight)
    position_size = 10000 / len(symbols)  # $10k portfolio

    print(f"\nPortfolio: ${10000:,.0f} equally weighted across {len(symbols)} stocks")
    print("\nScenario Analysis:")

    for scenario_name, market_move in scenarios.items():
        total_value = 0

        for _symbol, current_price in current_prices.items():
            shares = position_size / current_price
            new_price = current_price * (1 + market_move)
            new_value = shares * new_price
            total_value += new_value

        pnl = total_value - 10000
        pnl_pct = (pnl / 10000) * 100

        print(f"  {scenario_name:15s}: ${total_value:7,.0f} (${pnl:+7,.0f}, {pnl_pct:+5.1f}%)")

    print("=" * 60 + "\n")


# Main execution
async def main():
    """Run all custom examples."""
    print("\nProject Shri Sudarshan - Advanced Examples")
    print("=" * 60 + "\n")

    # Example 1: Custom agent
    print("1. Running custom volatility analyst...")
    await example_custom_agent()

    # Example 2: Custom workflow
    print("2. Running custom workflow...")
    await example_custom_workflow()

    # Example 3: Portfolio monitoring
    print("3. Portfolio monitoring...")
    await example_portfolio_monitoring()

    # Example 4: Scenario analysis
    print("4. Risk scenario analysis...")
    await example_risk_scenario_analysis()

    print("\nAll examples complete!")


if __name__ == "__main__":
    asyncio.run(main())
