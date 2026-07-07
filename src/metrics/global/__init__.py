"""Métricas globais de similaridade."""

from __future__ import annotations

from .simple_average import SimpleAverageMetric
from .weighted_average import WeightedAverageMetric

__all__ = [
    "SimpleAverageMetric",
    "WeightedAverageMetric",
]

