"""Strategy & Research Team agents."""

from .bearish import BearishResearcher
from .bullish import BullishResearcher
from .derivatives import DerivativesStrategist


__all__ = [
    "BullishResearcher",
    "BearishResearcher",
    "DerivativesStrategist",
]
