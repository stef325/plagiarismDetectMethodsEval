"""Funções auxiliares para métricas harmônicas."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
import re

from preprocessing.representation.harmony_representation import HarmonyRepresentation
from metrics.melody._helpers import (
    jaccard_similarity,
    levenshtein_distance,
    normalize_similarity_from_distance,
)


PITCH_CLASS_MAP = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
}


def build_chord_sequence(representation: HarmonyRepresentation) -> tuple[str, ...]:
    """Constrói a sequência de acordes da representação."""

    return tuple(event.chord for event in representation.harmony)


def build_ngrams(sequence: Sequence[str], n: int) -> Counter[tuple[str, ...]]:
    """Constrói n-grams de acordes a partir de uma sequência textual."""

    if n <= 0:
        raise ValueError("O tamanho do n-gram deve ser maior que zero.")
    if len(sequence) < n:
        return Counter()
    return Counter(tuple(sequence[index : index + n]) for index in range(len(sequence) - n + 1))


def parse_pitch_class_set(chord: str) -> frozenset[int]:
    """Converte um acorde em seu conjunto de classes de altura."""

    if not chord or chord.upper() in {"N.C.", "NC", "REST", "SILENCE"}:
        return frozenset()

    pitch_classes: set[int] = set()
    tokens = re.findall(r"([A-Ga-g])([#b]?)\d*", chord)
    if tokens:
        for note, accidental in tokens:
            pitch_class = PITCH_CLASS_MAP[note.upper()]
            if accidental == "#":
                pitch_class = (pitch_class + 1) % 12
            elif accidental == "b":
                pitch_class = (pitch_class - 1) % 12
            pitch_classes.add(pitch_class)
        return frozenset(pitch_classes)

    root_match = re.search(r"([A-Ga-g])([#b]?)", chord)
    if root_match is None:
        return frozenset()

    pitch_class = PITCH_CLASS_MAP[root_match.group(1).upper()]
    accidental = root_match.group(2)
    if accidental == "#":
        pitch_class = (pitch_class + 1) % 12
    elif accidental == "b":
        pitch_class = (pitch_class - 1) % 12
    return frozenset({pitch_class})


def build_pitch_class_sequence(representation: HarmonyRepresentation) -> tuple[frozenset[int], ...]:
    """Converte a sequência de acordes em conjuntos de classes de altura."""

    return tuple(parse_pitch_class_set(event.chord) for event in representation.harmony)


def pitch_class_sequence_similarity(
    left: Sequence[frozenset[int]],
    right: Sequence[frozenset[int]],
) -> float:
    """Compara duas sequências de classes de altura usando Jaccard por posição."""

    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0

    max_length = max(len(left), len(right))
    total = 0.0
    for index in range(max_length):
        left_set = left[index] if index < len(left) else frozenset()
        right_set = right[index] if index < len(right) else frozenset()
        if not left_set and not right_set:
            total += 1.0
            continue
        union = left_set | right_set
        if not union:
            total += 1.0
            continue
        total += len(left_set & right_set) / len(union)
    return total / max_length


def normalize_pitch_class_similarity(
    left: Sequence[frozenset[int]],
    right: Sequence[frozenset[int]],
) -> float:
    """Normaliza a comparação por classes de altura em um valor entre 0 e 1."""

    return pitch_class_sequence_similarity(left, right)


def chord_edit_distance_similarity(left: Sequence[str], right: Sequence[str]) -> float:
    """Calcula uma similaridade baseada em distância de edição para acordes."""

    distance = levenshtein_distance(left, right)
    return normalize_similarity_from_distance(distance, len(left), len(right))
