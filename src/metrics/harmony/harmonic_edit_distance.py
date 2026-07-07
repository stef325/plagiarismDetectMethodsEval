"""Métrica de similaridade baseada em distância de edição harmônica."""

from __future__ import annotations

from preprocessing.representation.harmony_representation import HarmonyRepresentation

from ._helpers import build_chord_sequence, chord_edit_distance_similarity


class HarmonicEditDistanceMetric:
    """Calcula a similaridade entre sequências de acordes por Levenshtein."""

    def compute(
        self,
        original: HarmonyRepresentation,
        transformed: HarmonyRepresentation,
    ) -> float:
        """Retorna uma similaridade normalizada entre 0 e 1."""

        original_chords = build_chord_sequence(original)
        transformed_chords = build_chord_sequence(transformed)
        return chord_edit_distance_similarity(original_chords, transformed_chords)

