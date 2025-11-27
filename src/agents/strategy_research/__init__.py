"""Strategy & Research Team agents."""

from .bearish import BearishResearcher
from .bullish import BullishResearcher
from .derivatives import DerivativesStrategist
from .reasoning import DeepSeekReasoningAgent


__all__ = [
    "BullishResearcher",
    "BearishResearcher",
    "DerivativesStrategist",
    "DeepSeekReasoningAgent",
]
