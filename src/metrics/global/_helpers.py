"""Funções auxiliares para métricas globais."""

from __future__ import annotations

from collections.abc import Mapping
from math import fsum, isclose


REQUIRED_WEIGHTS = ("melody", "harmony", "rhythm")


def validate_weights(weights: Mapping[str, float]) -> dict[str, float]:
    """Valida os pesos da métrica global.

    Args:
        weights: Pesos para melodia, harmonia e ritmo.

    Returns:
        Dicionário validado com os pesos.

    Raises:
        ValueError: Se faltar alguma chave, houver peso negativo ou a soma
            dos pesos for diferente de 1.0.
    """

    weight_keys = set(weights)
    required_keys = set(REQUIRED_WEIGHTS)

    missing_keys = required_keys - weight_keys
    if missing_keys:
        missing_list = ", ".join(sorted(missing_keys))
        raise ValueError(
            f"Pesos ausentes para a métrica global: {missing_list}."
        )

    unexpected_keys = weight_keys - required_keys
    if unexpected_keys:
        unexpected_list = ", ".join(sorted(unexpected_keys))
        raise ValueError(
            f"Pesos inesperados para a métrica global: {unexpected_list}."
        )

    normalized_weights = {key: float(weights[key]) for key in REQUIRED_WEIGHTS}
    negative_weights = [
        key for key, value in normalized_weights.items() if value < 0.0
    ]
    if negative_weights:
        negative_list = ", ".join(sorted(negative_weights))
        raise ValueError(
            f"Os seguintes pesos não podem ser negativos: {negative_list}."
        )

    total = fsum(normalized_weights.values())
    if not isclose(total, 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError(
            f"A soma dos pesos da métrica global deve ser 1.0, mas recebeu {total:.6f}."
        )

    return normalized_weights


def average_scores(scores: Mapping[str, float]) -> float:
    """Calcula a média aritmética de um conjunto de pontuações."""

    if not scores:
        return 1.0
    return fsum(scores.values()) / len(scores)


def flatten_scores(
    melody_scores: Mapping[str, float],
    harmony_scores: Mapping[str, float],
    rhythm_scores: Mapping[str, float],
) -> list[float]:
    """Agrupa todas as pontuações individuais em uma lista única."""

    values: list[float] = []
    values.extend(float(value) for value in melody_scores.values())
    values.extend(float(value) for value in harmony_scores.values())
    values.extend(float(value) for value in rhythm_scores.values())
    return values

