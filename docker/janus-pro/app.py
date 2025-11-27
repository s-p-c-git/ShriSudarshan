"""Janus-Pro Visual Analysis Service.

REST API for chart pattern recognition using Janus-Pro-7B.
"""

import base64
import io
import logging
import os
from typing import Any

from fastapi import FastAPI, HTTPException
from PIL import Image
from pydantic import BaseModel

from model import JanusProModel


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Janus-Pro Visual Analysis Service",
    description="Chart pattern recognition for Deep Reasoner v2.0",
    version="0.1.0",
)

# Global model instance
model: JanusProModel = None


class AnalyzeRequest(BaseModel):
    """Request model for chart analysis."""

    image: str  # Base64 encoded image
    prompt: str = "Analyze this chart for patterns."


class AnalyzeResponse(BaseModel):
    """Response model for chart analysis."""

    patterns: list[dict[str, Any]]
    confidence: float
    summary: str
    description: str
    trend: str
    levels: dict[str, list[float]]
    confluence: list[str]
    implications: str


@app.on_event("startup")
async def startup_event():
    """Load model on startup."""
    global model
    model_name = os.environ.get("MODEL_NAME", "deepseek-ai/Janus-Pro-7B")
    logger.info(f"Loading Janus-Pro model: {model_name}")
    model = JanusProModel(model_name)
    logger.info("Model loaded successfully")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model_loaded": model is not None}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_chart(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyze a chart image for patterns.

    Args:
        request: Contains base64 image and analysis prompt

    Returns:
        AnalyzeResponse with detected patterns
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Decode image
        image_data = base64.b64decode(request.image)
        image = Image.open(io.BytesIO(image_data))

        # Run analysis
        result = await model.analyze(image, request.prompt)

        return AnalyzeResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Model inference error: {e}")
        raise HTTPException(status_code=500, detail="Inference failed")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
