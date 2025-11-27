"""FinRL Execution Engine Service.

REST API for RL-based trade execution decisions.
"""

import logging
import os
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent import RLAgent


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FinRL Execution Engine",
    description="RL-based trade execution for Deep Reasoner v2.0",
    version="0.1.0",
)

# Global agent instance
agent: RLAgent = None


class PredictRequest(BaseModel):
    """Request model for execution prediction."""

    symbol: str
    state: dict[str, Any]
    agent_type: str = "ppo"


class PredictResponse(BaseModel):
    """Response model for execution prediction."""

    action: int  # -1: sell, 0: hold, 1: buy
    confidence: float
    amount: float
    timing: str
    slippage_estimate: float
    policy_output: dict[str, Any]


@app.on_event("startup")
async def startup_event():
    """Initialize RL agent on startup."""
    global agent
    agent_type = os.environ.get("AGENT_TYPE", "ppo")
    logger.info(f"Initializing RL agent: {agent_type}")
    agent = RLAgent(agent_type=agent_type)
    logger.info("Agent initialized successfully")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agent_loaded": agent is not None}


@app.post("/predict", response_model=PredictResponse)
async def predict_action(request: PredictRequest) -> PredictResponse:
    """
    Get execution action from RL agent.

    Args:
        request: Contains state vector and agent configuration

    Returns:
        PredictResponse with action and confidence
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not loaded")

    try:
        result = agent.predict(request.state)
        return PredictResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")


@app.post("/train")
async def train_agent(episodes: int = 100):
    """
    Train the RL agent.

    Args:
        episodes: Number of training episodes

    Returns:
        Training results
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not loaded")

    try:
        results = agent.train(episodes=episodes)
        return {"status": "training_complete", "results": results}
    except RuntimeError as e:
        logger.error(f"Training error: {e}")
        raise HTTPException(status_code=500, detail="Training failed")


@app.post("/save")
async def save_agent(path: str = "/app/policies/agent.zip"):
    """Save the trained agent."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not loaded")

    agent.save(path)
    return {"status": "saved", "path": path}


@app.post("/load")
async def load_agent(path: str = "/app/policies/agent.zip"):
    """Load a trained agent."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    agent.load(path)
    return {"status": "loaded", "path": path}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
