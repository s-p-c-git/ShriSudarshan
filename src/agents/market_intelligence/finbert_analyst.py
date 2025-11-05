"""Market Intelligence Team - FinBERT Sentiment Analyst.

This module provides high-speed, specialized sentiment analysis using the
FinBERT model pre-trained on financial text.
"""

from typing import Any

from ...data.schemas import AgentRole, FinBERTSentimentReport, Sentiment
from ...utils import get_logger


logger = get_logger(__name__)


class FinBERTSentimentAnalyst:
    """
    FinBERT Sentiment Analyst agent.

    Uses the ProsusAI/finbert pre-trained model from Hugging Face for
    high-accuracy sentiment classification of financial texts.
    """

    def __init__(self, model_name: str = "ProsusAI/finbert"):
        """
        Initialize the FinBERT Sentiment Analyst.

        Args:
            model_name: Hugging Face model name for FinBERT
        """
        self.role = AgentRole.FINBERT_SENTIMENT_ANALYST
        self.model_name = model_name
        self._model = None
        self._tokenizer = None

    def _load_model(self):
        """Lazy load the FinBERT model and tokenizer."""
        if self._model is None:
            try:
                from transformers import AutoModelForSequenceClassification, AutoTokenizer

                logger.info("Loading FinBERT model", model=self.model_name)
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self._model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
                logger.info("FinBERT model loaded successfully")
            except ImportError as e:
                logger.error(
                    "Failed to import transformers. Install with: pip install transformers torch"
                )
                raise ImportError(
                    "transformers library required for FinBERT. "
                    "Install with: pip install transformers torch"
                ) from e
            except Exception as e:
                logger.error("Failed to load FinBERT model", error=str(e))
                raise

    def _analyze_text(self, text: str) -> dict[str, float]:
        """
        Analyze sentiment of a single text using FinBERT.

        Args:
            text: Text to analyze

        Returns:
            Dict with sentiment scores: {positive, negative, neutral}
        """
        import torch

        self._load_model()

        # Tokenize input
        inputs = self._tokenizer(
            text, return_tensors="pt", padding=True, truncation=True, max_length=512
        )

        # Get predictions
        with torch.no_grad():
            outputs = self._model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

        # FinBERT outputs: [positive, negative, neutral]
        scores = predictions[0].tolist()
        return {"positive": scores[0], "negative": scores[1], "neutral": scores[2]}

    def _aggregate_sentiments(self, texts: list[str]) -> dict[str, Any]:
        """
        Aggregate sentiment scores from multiple texts.

        Args:
            texts: List of texts to analyze

        Returns:
            Dict with aggregated sentiment data
        """
        if not texts:
            return {
                "sentiment": "neutral",
                "positive": 0.33,
                "negative": 0.33,
                "neutral": 0.34,
                "confidence": 0.0,
            }

        total_positive = 0.0
        total_negative = 0.0
        total_neutral = 0.0

        for text in texts:
            scores = self._analyze_text(text)
            total_positive += scores["positive"]
            total_negative += scores["negative"]
            total_neutral += scores["neutral"]

        # Calculate averages
        count = len(texts)
        avg_positive = total_positive / count
        avg_negative = total_negative / count
        avg_neutral = total_neutral / count

        # Determine overall sentiment using argmax to avoid float equality issues
        avg_scores = {
            "positive": avg_positive,
            "negative": avg_negative,
            "neutral": avg_neutral,
        }
        sentiment = max(avg_scores, key=avg_scores.get)

        # Calculate confidence as the margin between top and second sentiment
        scores_sorted = sorted([avg_positive, avg_negative, avg_neutral], reverse=True)
        confidence = scores_sorted[0] - scores_sorted[1]

        return {
            "sentiment": sentiment,
            "positive": avg_positive,
            "negative": avg_negative,
            "neutral": avg_neutral,
            "confidence": confidence,
        }

    async def analyze(self, context: dict[str, Any]) -> FinBERTSentimentReport:
        """
        Analyze sentiment for financial texts using FinBERT.

        Args:
            context: Contains 'symbol', 'texts' (list of strings to analyze)

        Returns:
            FinBERTSentimentReport with sentiment analysis
        """
        symbol = context.get("symbol", "UNKNOWN")
        texts = context.get("texts", [])

        logger.info("Starting FinBERT sentiment analysis", symbol=symbol, text_count=len(texts))

        try:
            # Analyze texts
            result = self._aggregate_sentiments(texts)

            # Map to Sentiment enum
            sentiment_str = result["sentiment"]
            if sentiment_str == "positive":
                sentiment = Sentiment.BULLISH
            elif sentiment_str == "negative":
                sentiment = Sentiment.BEARISH
            else:
                sentiment = Sentiment.NEUTRAL

            # Calculate sentiment score from positive and negative
            sentiment_score = result["positive"] - result["negative"]

            # Create summary
            summary = (
                f"FinBERT analyzed {len(texts)} texts for {symbol}. "
                f"Overall sentiment: {sentiment_str} "
                f"(pos: {result['positive']:.2f}, neg: {result['negative']:.2f}, "
                f"neu: {result['neutral']:.2f})"
            )

            report = FinBERTSentimentReport(
                agent_role=AgentRole.FINBERT_SENTIMENT_ANALYST,
                symbol=symbol,
                summary=summary,
                confidence=result["confidence"],
                sentiment=sentiment,
                sentiment_score=sentiment_score,
                positive_score=result["positive"],
                negative_score=result["negative"],
                neutral_score=result["neutral"],
                text_analyzed=texts[:5],  # Store first 5 for reference
            )

            logger.info(
                "FinBERT sentiment analysis complete",
                symbol=symbol,
                sentiment=sentiment.value,
                score=sentiment_score,
                confidence=result["confidence"],
            )

            return report

        except Exception as e:
            logger.error("FinBERT sentiment analysis failed", symbol=symbol, error=str(e))

            return FinBERTSentimentReport(
                agent_role=AgentRole.FINBERT_SENTIMENT_ANALYST,
                symbol=symbol,
                summary=f"Analysis failed: {str(e)}",
                confidence=0.0,
                sentiment=Sentiment.NEUTRAL,
                sentiment_score=0.0,
                positive_score=0.33,
                negative_score=0.33,
                neutral_score=0.34,
                text_analyzed=[],
            )
