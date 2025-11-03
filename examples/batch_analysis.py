"""
Batch processing example: Analyze multiple stocks and generate reports.

This example demonstrates:
1. Batch analysis of multiple symbols
2. Parallel processing with rate limiting
3. Results aggregation and reporting
4. Export to CSV/JSON formats
"""

import asyncio
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.agents.market_intelligence import (
    FundamentalsAnalyst,
    MacroNewsAnalyst,
    SentimentAnalyst,
    TechnicalAnalyst,
)
from src.data.providers import MarketDataProvider, NewsProvider
from src.utils import get_logger, setup_logging


logger = get_logger(__name__)


class BatchAnalyzer:
    """Batch analyzer for multiple symbols."""

    def __init__(self, max_concurrent: int = 3):
        """
        Initialize batch analyzer.

        Args:
            max_concurrent: Maximum concurrent analyses (rate limiting)
        """
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

        # Initialize agents
        self.fundamentals_agent = FundamentalsAnalyst()
        self.technical_agent = TechnicalAnalyst()
        self.sentiment_agent = SentimentAnalyst()
        self.macro_agent = MacroNewsAnalyst()

        # Initialize data providers
        self.market_data = MarketDataProvider()
        self.news_provider = NewsProvider()

    async def analyze_symbol(self, symbol: str) -> dict[str, Any]:
        """
        Analyze a single symbol with all agents.

        Args:
            symbol: Stock ticker

        Returns:
            Dict containing all analysis results
        """
        async with self.semaphore:  # Rate limiting
            logger.info(f"Analyzing {symbol}")

            context = {
                "symbol": symbol,
                "market_data_provider": self.market_data,
                "news_provider": self.news_provider,
            }

            try:
                # Run all agents concurrently
                results = await asyncio.gather(
                    self.fundamentals_agent.analyze(context),
                    self.technical_agent.analyze(context),
                    self.sentiment_agent.analyze(context),
                    self.macro_agent.analyze(context),
                    return_exceptions=True,
                )

                fundamentals, technical, sentiment, macro = results

                # Extract key metrics
                analysis = {
                    "symbol": symbol,
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                    "error": None,
                }

                # Fundamentals
                if not isinstance(fundamentals, Exception):
                    analysis["fundamentals"] = {
                        "thesis": fundamentals.investment_thesis.value,
                        "confidence": fundamentals.confidence_level,
                        "key_points": fundamentals.key_points[:3],  # Top 3
                        "intrinsic_value": fundamentals.intrinsic_value,
                        "pe_ratio": fundamentals.financial_metrics.get("trailing_pe"),
                        "revenue_growth": fundamentals.financial_metrics.get("revenue_growth"),
                    }
                else:
                    logger.error(f"Fundamentals failed for {symbol}", error=str(fundamentals))
                    analysis["fundamentals"] = {"error": str(fundamentals)}

                # Technical
                if not isinstance(technical, Exception):
                    analysis["technical"] = {
                        "trend": technical.trend_direction.value,
                        "confidence": technical.confidence_level,
                        "support": technical.support_levels[:2],  # Top 2
                        "resistance": technical.resistance_levels[:2],
                        "rsi": technical.indicators.get("rsi"),
                        "patterns": technical.chart_patterns[:2],
                    }
                else:
                    logger.error(f"Technical failed for {symbol}", error=str(technical))
                    analysis["technical"] = {"error": str(technical)}

                # Sentiment
                if not isinstance(sentiment, Exception):
                    analysis["sentiment"] = {
                        "overall": sentiment.social_sentiment.value,
                        "confidence": sentiment.confidence_level,
                        "score": sentiment.sentiment_score,
                        "trending": sentiment.trending_topics[:3],
                    }
                else:
                    logger.error(f"Sentiment failed for {symbol}", error=str(sentiment))
                    analysis["sentiment"] = {"error": str(sentiment)}

                # Macro/News
                if not isinstance(macro, Exception):
                    analysis["macro"] = {
                        "sentiment": macro.market_sentiment.value,
                        "confidence": macro.confidence_level,
                        "key_events": macro.key_events[:3],
                        "themes": macro.macro_themes[:2],
                    }
                else:
                    logger.error(f"Macro failed for {symbol}", error=str(macro))
                    analysis["macro"] = {"error": str(macro)}

                # Calculate aggregate score
                confidences = []
                if "confidence" in analysis.get("fundamentals", {}):
                    confidences.append(analysis["fundamentals"]["confidence"])
                if "confidence" in analysis.get("technical", {}):
                    confidences.append(analysis["technical"]["confidence"])
                if "confidence" in analysis.get("sentiment", {}):
                    confidences.append(analysis["sentiment"]["confidence"])
                if "confidence" in analysis.get("macro", {}):
                    confidences.append(analysis["macro"]["confidence"])

                analysis["avg_confidence"] = (
                    sum(confidences) / len(confidences) if confidences else 0
                )

                # Determine consensus
                bullish_count = 0
                bearish_count = 0

                for key in ["fundamentals", "technical", "sentiment", "macro"]:
                    if key in analysis:
                        thesis_or_sentiment = (
                            analysis[key].get("thesis")
                            or analysis[key].get("overall")
                            or analysis[key].get("sentiment")
                        )
                        if thesis_or_sentiment:
                            if "bullish" in thesis_or_sentiment.lower():
                                bullish_count += 1
                            elif "bearish" in thesis_or_sentiment.lower():
                                bearish_count += 1

                if bullish_count > bearish_count:
                    analysis["consensus"] = "bullish"
                elif bearish_count > bullish_count:
                    analysis["consensus"] = "bearish"
                else:
                    analysis["consensus"] = "neutral"

                logger.info(
                    f"Analysis complete for {symbol}",
                    consensus=analysis["consensus"],
                    avg_confidence=f"{analysis['avg_confidence']:.1f}",
                )

                return analysis

            except Exception as e:
                logger.error(f"Analysis failed for {symbol}", error=str(e))
                return {
                    "symbol": symbol,
                    "timestamp": datetime.now().isoformat(),
                    "success": False,
                    "error": str(e),
                }

    async def analyze_batch(self, symbols: list[str]) -> list[dict[str, Any]]:
        """
        Analyze a batch of symbols.

        Args:
            symbols: List of stock tickers

        Returns:
            List of analysis results
        """
        logger.info(f"Starting batch analysis of {len(symbols)} symbols")

        tasks = [self.analyze_symbol(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)

        successful = sum(1 for r in results if r.get("success"))
        logger.info(f"Batch analysis complete: {successful}/{len(symbols)} successful")

        return results


def export_to_csv(results: list[dict[str, Any]], output_file: str):
    """
    Export analysis results to CSV.

    Args:
        results: List of analysis results
        output_file: Output CSV file path
    """
    if not results:
        logger.warning("No results to export")
        return

    # Define CSV columns
    fieldnames = [
        "symbol",
        "timestamp",
        "success",
        "consensus",
        "avg_confidence",
        "fundamentals_thesis",
        "fundamentals_confidence",
        "technical_trend",
        "technical_confidence",
        "sentiment_overall",
        "sentiment_confidence",
        "macro_sentiment",
        "macro_confidence",
        "error",
    ]

    with open(output_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            row = {
                "symbol": result.get("symbol"),
                "timestamp": result.get("timestamp"),
                "success": result.get("success"),
                "consensus": result.get("consensus"),
                "avg_confidence": f"{result.get('avg_confidence', 0):.1f}",
                "error": result.get("error"),
            }

            # Fundamentals
            if "fundamentals" in result:
                row["fundamentals_thesis"] = result["fundamentals"].get("thesis")
                row["fundamentals_confidence"] = result["fundamentals"].get("confidence")

            # Technical
            if "technical" in result:
                row["technical_trend"] = result["technical"].get("trend")
                row["technical_confidence"] = result["technical"].get("confidence")

            # Sentiment
            if "sentiment" in result:
                row["sentiment_overall"] = result["sentiment"].get("overall")
                row["sentiment_confidence"] = result["sentiment"].get("confidence")

            # Macro
            if "macro" in result:
                row["macro_sentiment"] = result["macro"].get("sentiment")
                row["macro_confidence"] = result["macro"].get("confidence")

            writer.writerow(row)

    logger.info(f"Results exported to {output_file}")


def export_to_json(results: list[dict[str, Any]], output_file: str):
    """
    Export analysis results to JSON.

    Args:
        results: List of analysis results
        output_file: Output JSON file path
    """
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    logger.info(f"Results exported to {output_file}")


def generate_summary_report(results: list[dict[str, Any]]):
    """
    Generate summary report of batch analysis.

    Args:
        results: List of analysis results
    """
    print("\n" + "=" * 80)
    print("BATCH ANALYSIS SUMMARY")
    print("=" * 80 + "\n")

    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]

    print(f"Total Symbols Analyzed: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")

    if failed:
        print("\nFailed Symbols:")
        for result in failed:
            print(f"  - {result['symbol']}: {result.get('error', 'Unknown error')}")

    if successful:
        # Consensus breakdown
        bullish = [r for r in successful if r.get("consensus") == "bullish"]
        bearish = [r for r in successful if r.get("consensus") == "bearish"]
        neutral = [r for r in successful if r.get("consensus") == "neutral"]

        print("\nConsensus Breakdown:")
        print(f"  Bullish: {len(bullish)} ({len(bullish)/len(successful)*100:.1f}%)")
        print(f"  Bearish: {len(bearish)} ({len(bearish)/len(successful)*100:.1f}%)")
        print(f"  Neutral: {len(neutral)} ({len(neutral)/len(successful)*100:.1f}%)")

        # Average confidence
        avg_conf = sum(r.get("avg_confidence", 0) for r in successful) / len(successful)
        print(f"\nAverage Confidence: {avg_conf:.1f}/10")

        # Top picks (highest confidence bullish)
        bullish_sorted = sorted(bullish, key=lambda x: x.get("avg_confidence", 0), reverse=True)

        print("\nTop Bullish Picks (High Confidence):")
        for result in bullish_sorted[:5]:
            symbol = result["symbol"]
            conf = result["avg_confidence"]
            print(f"  {symbol}: {conf:.1f}/10 confidence")

        # Top concerns (highest confidence bearish)
        bearish_sorted = sorted(bearish, key=lambda x: x.get("avg_confidence", 0), reverse=True)

        if bearish_sorted:
            print("\nTop Bearish Signals (High Confidence):")
            for result in bearish_sorted[:5]:
                symbol = result["symbol"]
                conf = result["avg_confidence"]
                print(f"  {symbol}: {conf:.1f}/10 confidence")

    print("\n" + "=" * 80 + "\n")


async def main():
    """Main execution function."""
    setup_logging()

    print("\nProject Shri Sudarshan - Batch Analysis")
    print("=" * 80 + "\n")

    # Define symbols to analyze
    symbols = [
        # Tech
        "AAPL",
        "GOOGL",
        "MSFT",
        "AMZN",
        "META",
        # Finance
        "JPM",
        "BAC",
        "GS",
        # Healthcare
        "JNJ",
        "UNH",
        "PFE",
        # Energy
        "XOM",
        "CVX",
        # Consumer
        "WMT",
        "HD",
        "NKE",
    ]

    print(f"Analyzing {len(symbols)} symbols...")
    print(f"Symbols: {', '.join(symbols)}\n")

    # Create analyzer with rate limiting (3 concurrent)
    analyzer = BatchAnalyzer(max_concurrent=3)

    # Run batch analysis
    start_time = datetime.now()
    results = await analyzer.analyze_batch(symbols)
    end_time = datetime.now()

    duration = (end_time - start_time).total_seconds()
    print(f"\nAnalysis completed in {duration:.1f} seconds")

    # Generate summary
    generate_summary_report(results)

    # Export results
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_file = output_dir / f"batch_analysis_{timestamp}.csv"
    json_file = output_dir / f"batch_analysis_{timestamp}.json"

    export_to_csv(results, str(csv_file))
    export_to_json(results, str(json_file))

    print("\nResults exported to:")
    print(f"  - {csv_file}")
    print(f"  - {json_file}")
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
