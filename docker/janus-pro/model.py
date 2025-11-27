"""Janus-Pro Model Wrapper.

Wrapper for Janus-Pro-7B visual understanding model.
Uses decoupled visual encoding for chart pattern recognition.
"""

import json
import logging
import os
from typing import Any

from PIL import Image


logger = logging.getLogger(__name__)


class JanusProModel:
    """
    Janus-Pro-7B model wrapper for chart analysis.

    Uses SigLIP-L encoder for visual understanding of candlestick charts.
    """

    def __init__(self, model_name: str = "deepseek-ai/Janus-Pro-7B"):
        """
        Initialize Janus-Pro model.

        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        self.model = None
        self.processor = None
        self._load_model()

    def _load_model(self):
        """Load the Janus-Pro model and processor."""
        try:
            from transformers import AutoModelForVision2Seq, AutoProcessor

            cache_dir = os.environ.get("MODEL_CACHE", "/app/model_cache")

            logger.info(f"Loading model from {self.model_name}")

            self.processor = AutoProcessor.from_pretrained(
                self.model_name,
                cache_dir=cache_dir,
                trust_remote_code=True,
            )

            self.model = AutoModelForVision2Seq.from_pretrained(
                self.model_name,
                cache_dir=cache_dir,
                trust_remote_code=True,
                device_map="auto",
            )

            logger.info("Model loaded successfully")

        except ImportError as e:
            logger.warning(f"Could not load model dependencies: {e}")
            logger.warning("Running in mock mode")
            self.model = None
            self.processor = None
        except RuntimeError as e:
            logger.warning(f"Could not load model: {e}")
            logger.warning("Running in mock mode")
            self.model = None
            self.processor = None

    async def analyze(self, image: Image.Image, prompt: str) -> dict[str, Any]:
        """
        Analyze a chart image.

        Args:
            image: PIL Image of the chart
            prompt: Analysis prompt

        Returns:
            Dictionary with analysis results
        """
        if self.model is None:
            # Return mock response for testing/fallback
            return self._mock_analysis(prompt)

        try:
            # Prepare inputs
            inputs = self.processor(
                images=image,
                text=prompt,
                return_tensors="pt",
            ).to(self.model.device)

            # Generate response
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=1024,
                temperature=0.3,
                do_sample=True,
            )

            # Decode response
            response = self.processor.decode(outputs[0], skip_special_tokens=True)

            # Parse structured response
            return self._parse_response(response)

        except RuntimeError as e:
            logger.error(f"Inference error: {e}")
            return self._mock_analysis(prompt)

    def _parse_response(self, response: str) -> dict[str, Any]:
        """
        Parse model response into structured format.

        Args:
            response: Raw model output

        Returns:
            Structured analysis dictionary
        """
        # Try to extract JSON if present - handle nested objects
        # First try to find JSON in code blocks
        if "```json" in response:
            try:
                json_str = response.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            except (json.JSONDecodeError, IndexError):
                pass
        elif "```" in response:
            try:
                json_str = response.split("```")[1].split("```")[0].strip()
                return json.loads(json_str)
            except (json.JSONDecodeError, IndexError):
                pass

        # Try to find balanced braces for JSON object
        try:
            start_idx = response.find("{")
            if start_idx != -1:
                depth = 0
                end_idx = start_idx
                for i, char in enumerate(response[start_idx:], start_idx):
                    if char == "{":
                        depth += 1
                    elif char == "}":
                        depth -= 1
                        if depth == 0:
                            end_idx = i
                            break
                if depth == 0 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx + 1]
                    return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass

        # Parse free-form response
        patterns = []

        # Look for pattern mentions
        pattern_keywords = [
            "head and shoulders",
            "double top",
            "double bottom",
            "triangle",
            "wedge",
            "flag",
            "pennant",
            "cup and handle",
            "ascending channel",
            "descending channel",
        ]

        response_lower = response.lower()
        for keyword in pattern_keywords:
            if keyword in response_lower:
                patterns.append({
                    "name": keyword.title(),
                    "confidence": 0.7,
                    "stage": "detected",
                })

        # Determine trend
        trend = "neutral"
        if "uptrend" in response_lower or "bullish" in response_lower:
            trend = "bullish"
        elif "downtrend" in response_lower or "bearish" in response_lower:
            trend = "bearish"

        return {
            "patterns": patterns,
            "confidence": 0.5 if not patterns else 0.7,
            "summary": response[:200],
            "description": response,
            "trend": trend,
            "levels": {"support": [], "resistance": []},
            "confluence": [],
            "implications": "Based on visual pattern analysis",
        }

    def _mock_analysis(self, prompt: str) -> dict[str, Any]:
        """
        Return mock analysis for testing.

        Args:
            prompt: Original prompt

        Returns:
            Mock analysis result
        """
        return {
            "patterns": [
                {
                    "name": "Potential Support Level",
                    "confidence": 0.6,
                    "stage": "forming",
                }
            ],
            "confidence": 0.5,
            "summary": "Mock analysis: Model not loaded or unavailable",
            "description": "This is a mock response for testing purposes.",
            "trend": "neutral",
            "levels": {"support": [], "resistance": []},
            "confluence": [],
            "implications": "Model unavailable - manual review recommended",
        }
