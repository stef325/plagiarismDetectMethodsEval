"""Métrica de similaridade baseada em IOI."""

from __future__ import annotations

from preprocessing.representation.rhythm_representation import RhythmRepresentation

from ._helpers import build_ioi_sequence, sequence_similarity


class IoISimilarityMetric:
    """Compara representações rítmicas pela sequência de inter-onset intervals."""

    def compute(
        self,
        original: RhythmRepresentation,
        transformed: RhythmRepresentation,
    ) -> float:
        """Retorna uma similaridade normalizada entre 0 e 1."""

        original_ioi = build_ioi_sequence(original)
        transformed_ioi = build_ioi_sequence(transformed)
        return sequence_similarity(original_ioi, transformed_ioi)

