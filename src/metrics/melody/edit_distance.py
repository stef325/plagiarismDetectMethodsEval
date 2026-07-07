"""Métrica de similaridade baseada em distância de edição."""

from __future__ import annotations

from preprocessing.representation.melody_representation import MelodyRepresentation

from ._helpers import (
    build_melodic_interval_sequence,
    levenshtein_distance,
    normalize_similarity_from_distance,
)


class EditDistanceMetric:
    """Calcula a similaridade melódica a partir da distância de Levenshtein."""

    def compute(
        self,
        original: MelodyRepresentation,
        transformed: MelodyRepresentation,
    ) -> float:
        """Retorna um índice de similaridade normalizado entre 0 e 1."""

        original_sequence = build_melodic_interval_sequence(original)
        transformed_sequence = build_melodic_interval_sequence(transformed)
        distance = levenshtein_distance(original_sequence, transformed_sequence)
        return normalize_similarity_from_distance(
            distance=distance,
            left_size=len(original_sequence),
            right_size=len(transformed_sequence),
        )

