"""Métrica de similaridade por n-grams de acordes."""

from __future__ import annotations

from preprocessing.representation.harmony_representation import HarmonyRepresentation

from ._helpers import build_chord_sequence, build_ngrams
from metrics.melody._helpers import jaccard_similarity


class ChordNGramSimilarityMetric:
    """Calcula similaridade harmônica com base em n-grams de acordes."""

    def compute(
        self,
        original: HarmonyRepresentation,
        transformed: HarmonyRepresentation,
        n: int = 2,
    ) -> float:
        """Retorna a similaridade normalizada entre duas sequências de acordes."""

        original_chords = build_chord_sequence(original)
        transformed_chords = build_chord_sequence(transformed)

        original_ngrams = build_ngrams(original_chords, n)
        transformed_ngrams = build_ngrams(transformed_chords, n)

        if not original_ngrams and not transformed_ngrams:
            return 1.0 if original_chords == transformed_chords else 0.0
        if not original_ngrams or not transformed_ngrams:
            return 0.0
        return jaccard_similarity(original_ngrams, transformed_ngrams)

