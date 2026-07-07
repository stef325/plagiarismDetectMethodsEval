"""Métrica de similaridade por n-grams de intervalos."""

from __future__ import annotations

from preprocessing.representation.melody_representation import MelodyRepresentation

from ._helpers import build_melodic_interval_sequence, build_ngrams, jaccard_similarity


class IntervalNGramSimilarityMetric:
    """Calcula similaridade melódica a partir de n-grams intervalares."""

    def compute(
        self,
        original: MelodyRepresentation,
        transformed: MelodyRepresentation,
        n: int = 2,
    ) -> float:
        """Calcula a similaridade entre duas melodias usando n-grams de intervalos."""

        original_intervals = build_melodic_interval_sequence(original)
        transformed_intervals = build_melodic_interval_sequence(transformed)

        original_ngrams = build_ngrams(original_intervals, n)
        transformed_ngrams = build_ngrams(transformed_intervals, n)

        if not original_ngrams and not transformed_ngrams:
            return 1.0 if original_intervals == transformed_intervals else 0.0
        if not original_ngrams or not transformed_ngrams:
            return 0.0
        return jaccard_similarity(original_ngrams, transformed_ngrams)

