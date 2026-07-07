"""Métrica de similaridade por classes de altura."""

from __future__ import annotations

from preprocessing.representation.harmony_representation import HarmonyRepresentation

from ._helpers import build_pitch_class_sequence, normalize_pitch_class_similarity


class PitchClassSimilarityMetric:
    """Compara representações harmônicas ignorando oitavas."""

    def compute(
        self,
        original: HarmonyRepresentation,
        transformed: HarmonyRepresentation,
    ) -> float:
        """Retorna uma similaridade normalizada entre 0 e 1."""

        original_pitch_classes = build_pitch_class_sequence(original)
        transformed_pitch_classes = build_pitch_class_sequence(transformed)
        return normalize_pitch_class_similarity(original_pitch_classes, transformed_pitch_classes)

