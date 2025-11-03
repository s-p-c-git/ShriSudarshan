"""
Simple example of running the trading workflow.

This example demonstrates how to use the Project Shri Sudarshan
system programmatically rather than through the CLI.
"""

import asyncio
import sys
from pathlib import Path


# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from orchestration import TradingWorkflow
from utils import get_logger, setup_logging


async def run_simple_analysis():
    """Run a simple analysis workflow."""
    # Setup logging
    setup_logging()
    logger = get_logger(__name__)

    # Create workflow
    workflow = TradingWorkflow()

    # Run analysis for a symbol
    symbol = "AAPL"
    logger.info(f"Starting analysis for {symbol}")

    try:
        result = await workflow.run(symbol=symbol)

        # Print results
        print("\n" + "=" * 60)
        print(f"Analysis Results for {symbol}")
        print("=" * 60)
        print(f"Analysis Complete: {result.get('analysis_complete', False)}")
        print(f"Debate Complete: {result.get('debate_complete', False)}")
        print(f"Strategy Complete: {result.get('strategy_complete', False)}")
        print(f"Risk Approved: {result.get('risk_approved', False)}")
        print(f"Final Approval: {result.get('final_approval', False)}")
        print(f"Execution Complete: {result.get('execution_complete', False)}")
        print("=" * 60 + "\n")

        return result

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise


async def run_multiple_symbols():
    """Analyze multiple symbols sequentially."""
    symbols = ["AAPL", "GOOGL", "MSFT"]
    workflow = TradingWorkflow()

    results = {}
    for symbol in symbols:
        print(f"\nAnalyzing {symbol}...")
        result = await workflow.run(symbol=symbol)
        results[symbol] = result

    return results


if __name__ == "__main__":
    print("Project Shri Sudarshan - Simple Example")
    print("=" * 60)

    # Run single analysis
    result = asyncio.run(run_simple_analysis())

    # Uncomment to analyze multiple symbols
    # results = asyncio.run(run_multiple_symbols())
