"""Média ponderada para métricas globais."""

from __future__ import annotations

from collections.abc import Mapping

from ._helpers import average_scores, validate_weights


class WeightedAverageMetric:
    """Calcula a média ponderada das métricas individuais."""

    def compute(
        self,
        melody_scores: Mapping[str, float],
        harmony_scores: Mapping[str, float],
        rhythm_scores: Mapping[str, float],
        weights: Mapping[str, float],
    ) -> float:
        """Calcula a média ponderada entre as três modalidades."""

        validated_weights = validate_weights(weights)
        melody_average = average_scores(melody_scores)
        harmony_average = average_scores(harmony_scores)
        rhythm_average = average_scores(rhythm_scores)

        return (
            melody_average * validated_weights["melody"]
            + harmony_average * validated_weights["harmony"]
            + rhythm_average * validated_weights["rhythm"]
        )

