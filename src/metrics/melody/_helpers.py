"""Funções auxiliares para métricas melódicas."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

from preprocessing.representation.melody_representation import MelodyRepresentation


def build_melodic_interval_sequence(representation: MelodyRepresentation) -> tuple[int, ...]:
    """Constrói a sequência de intervalos entre notas consecutivas."""

    pitches = [note.pitch for note in representation.notes]
    return tuple(current - previous for previous, current in zip(pitches, pitches[1:]))


def build_ngrams(sequence: Sequence[int], n: int) -> Counter[tuple[int, ...]]:
    """Constrói n-grams a partir de uma sequência numérica."""

    if n <= 0:
        raise ValueError("O tamanho do n-gram deve ser maior que zero.")
    if len(sequence) < n:
        return Counter()
    return Counter(tuple(sequence[index : index + n]) for index in range(len(sequence) - n + 1))


def jaccard_similarity(left: Counter[tuple[int, ...]], right: Counter[tuple[int, ...]]) -> float:
    """Calcula a similaridade de Jaccard entre multiconjuntos."""

    if not left and not right:
        return 1.0

    all_keys = set(left) | set(right)
    intersection = sum(min(left[key], right[key]) for key in all_keys)
    union = sum(max(left[key], right[key]) for key in all_keys)
    if union == 0:
        return 1.0
    return intersection / union


def longest_common_subsequence_length(left: Sequence[int], right: Sequence[int]) -> int:
    """Calcula o comprimento da maior subsequência comum."""

    if not left or not right:
        return 0

    previous_row = [0] * (len(right) + 1)
    for left_value in left:
        current_row = [0]
        for index, right_value in enumerate(right, start=1):
            if left_value == right_value:
                current_row.append(previous_row[index - 1] + 1)
            else:
                current_row.append(max(previous_row[index], current_row[-1]))
        previous_row = current_row
    return previous_row[-1]


def levenshtein_distance(left: Sequence[int], right: Sequence[int]) -> int:
    """Calcula a distância de edição entre duas sequências."""

    if not left:
        return len(right)
    if not right:
        return len(left)

    previous_row = list(range(len(right) + 1))
    for left_index, left_value in enumerate(left, start=1):
        current_row = [left_index]
        for right_index, right_value in enumerate(right, start=1):
            insertion_cost = current_row[right_index - 1] + 1
            deletion_cost = previous_row[right_index] + 1
            substitution_cost = previous_row[right_index - 1] + (left_value != right_value)
            current_row.append(min(insertion_cost, deletion_cost, substitution_cost))
        previous_row = current_row
    return previous_row[-1]


def normalize_similarity_from_distance(distance: int, left_size: int, right_size: int) -> float:
    """Normaliza uma distância para uma similaridade entre 0 e 1."""

    max_size = max(left_size, right_size)
    if max_size == 0:
        return 1.0
    similarity = 1.0 - (distance / max_size)
    return max(0.0, min(1.0, similarity))
