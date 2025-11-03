"""
Main entry point for Project Shri Sudarshan.

This script provides a CLI interface to run the trading system.
"""

import argparse
import asyncio
import sys
from pathlib import Path


# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from orchestration import TradingWorkflow
from utils import get_logger, setup_logging


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Project Shri Sudarshan: Hybrid Multi-Agent LLM Trading System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single symbol
  python main.py --symbol AAPL

  # Analyze with date range
  python main.py --symbol AAPL --start_date 2023-01-01 --end_date 2023-01-31

  # Run in paper trading mode (default)
  python main.py --symbol AAPL --paper-trading
        """,
    )

    parser.add_argument(
        "--symbol",
        type=str,
        required=True,
        help="Stock symbol to analyze (e.g., AAPL, TSLA)",
    )

    parser.add_argument(
        "--start_date",
        type=str,
        default=None,
        help="Start date for analysis (YYYY-MM-DD)",
    )

    parser.add_argument(
        "--end_date", type=str, default=None, help="End date for analysis (YYYY-MM-DD)"
    )

    parser.add_argument(
        "--paper-trading",
        action="store_true",
        default=True,
        help="Enable paper trading mode (default: True)",
    )

    parser.add_argument(
        "--live-trading",
        action="store_true",
        default=False,
        help="Enable live trading mode (CAUTION: Real money!)",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    return parser.parse_args()


async def main():
    """Main execution function."""
    # Parse arguments
    args = parse_args()

    # Setup logging
    setup_logging()
    logger = get_logger(__name__)

    # Log startup
    logger.info(
        "Starting Project Shri Sudarshan",
        symbol=args.symbol,
        start_date=args.start_date,
        end_date=args.end_date,
        paper_trading=not args.live_trading,
    )

    # Validate API key
    if (
        not settings.openai_api_key
        or settings.openai_api_key == "your_openai_api_key_here"
        or settings.openai_api_key == "test-key-not-set"
    ):
        logger.error("OpenAI API key not configured. Please set OPENAI_API_KEY in .env file")
        print("\nError: OpenAI API key not configured!")
        print("Please copy .env.example to .env and add your API key.")
        return 1

    # Warning for live trading
    if args.live_trading:
        logger.warning("LIVE TRADING MODE ENABLED - REAL MONEY AT RISK")
        print("\n" + "=" * 60)
        print("WARNING: LIVE TRADING MODE ENABLED")
        print("=" * 60)
        response = input("Are you sure you want to proceed? (yes/no): ")
        if response.lower() != "yes":
            logger.info("Live trading cancelled by user")
            return 0

    try:
        # Initialize workflow
        workflow = TradingWorkflow()

        # Run the trading workflow
        logger.info("Initializing trading workflow", symbol=args.symbol)

        result = await workflow.run(
            symbol=args.symbol,
            start_date=args.start_date,
            end_date=args.end_date,
        )

        # Log results
        logger.info(
            "Workflow completed successfully",
            symbol=args.symbol,
            final_phase=result.get("current_phase"),
            approved=result.get("final_approval", False),
        )

        # Print summary
        print("\n" + "=" * 60)
        print("WORKFLOW SUMMARY")
        print("=" * 60)
        print(f"Symbol: {result.get('symbol')}")
        print(f"Final Phase: {result.get('current_phase')}")
        print(f"Analysis Complete: {result.get('analysis_complete', False)}")
        print(f"Debate Complete: {result.get('debate_complete', False)}")
        print(f"Strategy Complete: {result.get('strategy_complete', False)}")
        print(f"Risk Approved: {result.get('risk_approved', False)}")
        print(f"Final Approval: {result.get('final_approval', False)}")
        print(f"Execution Complete: {result.get('execution_complete', False)}")

        if result.get("errors"):
            print("\nErrors encountered:")
            for error in result["errors"]:
                print(f"  - {error}")

        print("=" * 60 + "\n")

        return 0

    except KeyboardInterrupt:
        logger.info("Workflow interrupted by user")
        print("\nWorkflow interrupted by user")
        return 130

    except Exception as e:
        logger.error("Workflow failed with error", error=str(e), exc_info=True)
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
