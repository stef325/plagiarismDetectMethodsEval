"""Métrica de similaridade baseada em LCS."""

from __future__ import annotations

from preprocessing.representation.melody_representation import MelodyRepresentation

from ._helpers import (
    build_melodic_interval_sequence,
    longest_common_subsequence_length,
)


class LongestCommonSubsequenceMetric:
    """Calcula a similaridade pela maior subsequência comum."""

    def compute(
        self,
        original: MelodyRepresentation,
        transformed: MelodyRepresentation,
    ) -> float:
        """Retorna a similaridade normalizada entre duas melodias."""

        original_sequence = build_melodic_interval_sequence(original)
        transformed_sequence = build_melodic_interval_sequence(transformed)

        if not original_sequence and not transformed_sequence:
            return 1.0

        lcs_length = longest_common_subsequence_length(original_sequence, transformed_sequence)
        return lcs_length / max(len(original_sequence), len(transformed_sequence))

