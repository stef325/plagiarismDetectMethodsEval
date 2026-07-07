"""Métrica de similaridade por n-grams rítmicos."""

from __future__ import annotations

from preprocessing.representation.rhythm_representation import RhythmRepresentation

from ._helpers import build_ngrams, build_rhythm_sequence, ngram_similarity


class RhythmNGramSimilarityMetric:
    """Calcula similaridade rítmica a partir de n-grams de eventos."""

    def compute(
        self,
        original: RhythmRepresentation,
        transformed: RhythmRepresentation,
        n: int = 2,
    ) -> float:
        """Retorna a similaridade normalizada entre duas sequências rítmicas."""

        original_sequence = build_rhythm_sequence(original)
        transformed_sequence = build_rhythm_sequence(transformed)
        original_ngrams = build_ngrams(original_sequence, n)
        transformed_ngrams = build_ngrams(transformed_sequence, n)

        if not original_ngrams and not transformed_ngrams:
            return 1.0 if original_sequence == transformed_sequence else 0.0
        if not original_ngrams or not transformed_ngrams:
            return 0.0
        return ngram_similarity(original_ngrams, transformed_ngrams)

