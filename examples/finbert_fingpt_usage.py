"""
Example: Using FinBERT and FinGPT Analysts

This script demonstrates how to use the new FinBERT and FinGPT agents
for financial sentiment analysis and generative insights.
"""

import asyncio
from src.agents.market_intelligence import (
    FinBERTSentimentAnalyst,
    FinGPTGenerativeAnalyst,
)


async def finbert_example():
    """Example of using FinBERT for sentiment analysis."""
    print("\n=== FinBERT Sentiment Analysis Example ===\n")

    # Initialize the analyst
    analyst = FinBERTSentimentAnalyst()

    # Example financial news headlines
    news_headlines = [
        "Apple reports record quarterly earnings, beating analyst expectations",
        "Tech giant announces $100B stock buyback program",
        "Market analysts upgrade AAPL to strong buy rating",
        "New product launch receives positive early reviews",
    ]

    # Prepare context
    context = {
        "symbol": "AAPL",
        "texts": news_headlines,
    }

    # Analyze sentiment
    report = await analyst.analyze(context)

    # Display results
    print(f"Symbol: {report.symbol}")
    print(f"Overall Sentiment: {report.sentiment.value}")
    print(f"Sentiment Score: {report.sentiment_score:.3f} (range: -1 to +1)")
    print(f"\nDetailed Scores:")
    print(f"  Positive: {report.positive_score:.3f}")
    print(f"  Negative: {report.negative_score:.3f}")
    print(f"  Neutral: {report.neutral_score:.3f}")
    print(f"\nConfidence: {report.confidence:.3f}")
    print(f"\nSummary: {report.summary}")


async def fingpt_example():
    """Example of using FinGPT for generative analysis."""
    print("\n=== FinGPT Generative Analysis Example ===\n")

    # Initialize the analyst (using non-local mode for demo)
    analyst = FinGPTGenerativeAnalyst(use_local=False)

    # Example financial text
    financial_text = """
    Apple Inc. reported strong Q3 2024 results with revenue of $85.7B,
    up 15% year-over-year. iPhone revenue grew 18% to $51.2B, driven by
    strong demand for the new iPhone 15 Pro models. Services revenue
    reached a new record of $21.2B, up 12% YoY.
    
    The company announced a new $100B share repurchase authorization and
    increased the dividend by 8%. Management expressed confidence in the
    upcoming product cycle and expansion in emerging markets.
    
    Gross margin improved to 45.2% from 43.1% a year ago, reflecting
    favorable mix and operational improvements. Operating margin expanded
    180 basis points to 28.5%.
    """

    # Prepare context for different analysis types
    contexts = [
        {
            "symbol": "AAPL",
            "text": financial_text,
            "analysis_type": "general_analysis",
        },
        {
            "symbol": "AAPL",
            "text": financial_text,
            "analysis_type": "summarize_filing",
        },
    ]

    for context in contexts:
        report = await analyst.analyze(context)

        print(f"\nAnalysis Type: {report.analysis_type}")
        print(f"Symbol: {report.symbol}")
        print(f"Confidence: {report.confidence:.3f}")

        print(f"\nKey Insights:")
        for i, insight in enumerate(report.key_insights, 1):
            print(f"  {i}. {insight}")

        print(f"\nRisks Identified:")
        for i, risk in enumerate(report.risks_identified, 1):
            print(f"  {i}. {risk}")

        print(f"\nOpportunities Identified:")
        for i, opp in enumerate(report.opportunities_identified, 1):
            print(f"  {i}. {opp}")

        print(f"\nSummary: {report.summary}")
        print("\n" + "=" * 60)


async def combined_example():
    """Example showing how both agents work together."""
    print("\n=== Combined Analysis: FinBERT + FinGPT ===\n")

    # Initialize both analysts
    finbert = FinBERTSentimentAnalyst()
    fingpt = FinGPTGenerativeAnalyst(use_local=False)

    # Sample news articles
    news_articles = [
        "Apple faces increased competition in smartphone market",
        "Supply chain concerns impact iPhone production estimates",
        "Analyst downgrades AAPL citing valuation concerns",
    ]

    # Step 1: FinBERT for rapid sentiment screening
    print("Step 1: FinBERT Sentiment Screening")
    sentiment_context = {"symbol": "AAPL", "texts": news_articles}
    sentiment_report = await finbert.analyze(sentiment_context)

    print(f"  Sentiment: {sentiment_report.sentiment.value}")
    print(f"  Score: {sentiment_report.sentiment_score:.3f}")

    # Step 2: If sentiment is strongly negative, trigger FinGPT for deep analysis
    if sentiment_report.sentiment_score < -0.3:
        print("\n⚠ Strong negative sentiment detected!")
        print("Step 2: FinGPT Deep Dive Analysis")

        deep_analysis_context = {
            "symbol": "AAPL",
            "texts": news_articles,
            "analysis_type": "analyze_news",
        }
        analysis_report = await fingpt.analyze(deep_analysis_context)

        print(f"\nDeep Analysis Results:")
        print(f"  Key Insights: {len(analysis_report.key_insights)} identified")
        print(f"  Risks: {len(analysis_report.risks_identified)} identified")
        print(f"  Opportunities: {len(analysis_report.opportunities_identified)} identified")

        print(f"\nActionable Intelligence:")
        for insight in analysis_report.key_insights:
            print(f"  • {insight}")
    else:
        print("\nℹ No deep dive needed - sentiment within normal range")


async def main():
    """Run all examples."""
    print("=" * 70)
    print("FinBERT and FinGPT Integration Examples")
    print("=" * 70)

    try:
        # Run examples
        await finbert_example()
        await fingpt_example()
        await combined_example()

        print("\n" + "=" * 70)
        print("Examples completed successfully!")
        print("=" * 70)

    except ImportError as e:
        print(f"\n⚠ Import Error: {e}")
        print("\nPlease install required dependencies:")
        print("  pip install transformers torch accelerate bitsandbytes")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nNote: These examples use mock data when actual models are not available.")


if __name__ == "__main__":
    asyncio.run(main())
