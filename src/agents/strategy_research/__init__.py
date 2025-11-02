"""Strategy & Research Team agents."""

from .bullish import BullishResearcher
from .bearish import BearishResearcher
from .derivatives import DerivativesStrategist

__all__ = [
    "BullishResearcher",
    "BearishResearcher",
    "DerivativesStrategist",
]
