"""Funções auxiliares para métricas rítmicas."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

from preprocessing.representation.rhythm_representation import RhythmRepresentation
from metrics.melody._helpers import (
    jaccard_similarity,
    levenshtein_distance,
    normalize_similarity_from_distance,
)


def build_rhythm_sequence(representation: RhythmRepresentation) -> tuple[tuple[float, float], ...]:
    """Constrói uma sequência rítmica normalizada por escala temporal."""

    if not representation.rhythm:
        return ()

    span = max(event.onset + event.duration for event in representation.rhythm)
    if span <= 0:
        span = 1.0

    return tuple(
        (event.onset / span, event.duration / span)
        for event in representation.rhythm
    )


def build_ngrams(sequence: Sequence[tuple[float, float]], n: int) -> Counter[tuple[tuple[float, float], ...]]:
    """Constrói n-grams a partir de uma sequência de eventos rítmicos."""

    if n <= 0:
        raise ValueError("O tamanho do n-gram deve ser maior que zero.")
    if len(sequence) < n:
        return Counter()
    return Counter(tuple(sequence[index : index + n]) for index in range(len(sequence) - n + 1))


def build_ioi_sequence(representation: RhythmRepresentation) -> tuple[float, ...]:
    """Calcula a sequência de IOIs entre onsets consecutivos."""

    onsets = [event.onset for event in representation.rhythm]
    if not onsets:
        return ()

    span = max((event.onset + event.duration) for event in representation.rhythm)
    if span <= 0:
        span = 1.0
    normalized_onsets = [onset / span for onset in onsets]
    return tuple(
        current - previous
        for previous, current in zip(normalized_onsets, normalized_onsets[1:])
    )


def sequence_similarity(
    left: Sequence[float],
    right: Sequence[float],
    tolerance: float = 1e-6,
) -> float:
    """Compara duas sequências numéricas alinhadas por posição."""

    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0

    max_length = max(len(left), len(right))
    total = 0.0
    for index in range(max_length):
        left_value = left[index] if index < len(left) else None
        right_value = right[index] if index < len(right) else None
        if left_value is None or right_value is None:
            continue
        if abs(left_value - right_value) <= tolerance:
            total += 1.0
            continue
        denominator = max(abs(left_value), abs(right_value), tolerance)
        total += max(0.0, 1.0 - (abs(left_value - right_value) / denominator))
    return total / max_length


def ngram_similarity(
    left: Counter[tuple[object, ...]],
    right: Counter[tuple[object, ...]],
) -> float:
    """Calcula a similaridade de Jaccard entre n-grams."""

    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return jaccard_similarity(left, right)


def edit_distance_similarity(left: Sequence[object], right: Sequence[object]) -> float:
    """Calcula uma similaridade normalizada a partir da distância de edição."""

    distance = levenshtein_distance(left, right)
    return normalize_similarity_from_distance(distance, len(left), len(right))
