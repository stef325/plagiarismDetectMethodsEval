"""Média simples para métricas globais."""

from __future__ import annotations

from collections.abc import Mapping

from ._helpers import flatten_scores


class SimpleAverageMetric:
    """Calcula a média aritmética simples das métricas individuais."""

    def compute(
        self,
        melody_scores: Mapping[str, float],
        harmony_scores: Mapping[str, float],
        rhythm_scores: Mapping[str, float],
    ) -> float:
        """Calcula a média simples entre todas as pontuações disponíveis."""

        values = flatten_scores(melody_scores, harmony_scores, rhythm_scores)
        if not values:
            return 1.0
        return sum(values) / len(values)

