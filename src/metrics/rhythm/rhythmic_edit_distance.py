"""Métrica de similaridade baseada em distância de edição rítmica."""

from __future__ import annotations

from preprocessing.representation.rhythm_representation import RhythmRepresentation

from ._helpers import build_rhythm_sequence, edit_distance_similarity


class RhythmicEditDistanceMetric:
    """Calcula a similaridade entre sequências rítmicas por Levenshtein."""

    def compute(
        self,
        original: RhythmRepresentation,
        transformed: RhythmRepresentation,
    ) -> float:
        """Retorna uma similaridade normalizada entre 0 e 1."""

        original_sequence = build_rhythm_sequence(original)
        transformed_sequence = build_rhythm_sequence(transformed)
        return edit_distance_similarity(original_sequence, transformed_sequence)

