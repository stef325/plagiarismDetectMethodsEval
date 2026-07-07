"""Utilitários internos para transformações combinadas."""

from __future__ import annotations

from typing import Any


CATEGORY_ALIASES = {
    "melody": "m",
    "harmony": "h",
    "rhythm": "r",
}

TRANSFORMATION_ALIASES = {
    "transpose": "t",
    "interval_modification": "im",
    "ornamentation": "orn",
    "simplification": "s",
    "chord_substitution": "cs",
    "reharmonization": "reh",
    "tempo_change": "tc",
    "duration_scaling": "ds",
    "partial_rhythm_modification": "prm",
}

COMBINATION_ALIASES = {
    "melody_harmony": "mh",
    "melody_rhythm": "mr",
    "harmony_rhythm": "hr",
    "melody_harmony_rhythm": "mhr",
}


def build_parameter_signature(parameters: dict[str, Any]) -> str:
    """Cria um identificador textual compacto para parâmetros aninhados."""

    ordered_items = sorted(parameters.items())
    parts = [f"{key}_{normalize_parameter_value(value)}" for key, value in ordered_items]
    return "__".join(parts)


def build_combination_signature(combination_name: str, combination_spec: dict[str, Any]) -> str:
    """Cria uma assinatura compacta para uma combinação."""

    ordered_categories = sorted(combination_spec.items())
    parts = []
    for category, spec in ordered_categories:
        if not isinstance(spec, dict):
            continue
        alias = CATEGORY_ALIASES.get(category, category[:1])
        transformation = str(spec.get("transformation", "unknown"))
        transformation_alias = TRANSFORMATION_ALIASES.get(transformation, transformation[:3])
        parameters = spec.get("parameters", {})
        parameter_signature = build_parameter_signature(parameters) if isinstance(parameters, dict) else "no_params"
        parts.append(f"{alias}{transformation_alias}_{parameter_signature}")
    prefix = COMBINATION_ALIASES.get(combination_name, combination_name[:3])
    return prefix if not parts else prefix + "__" + "__".join(parts)


def normalize_parameter_value(value: Any) -> str:
    """Normaliza um valor para uso em caminho de arquivo."""

    if isinstance(value, float):
        return f"{value}".replace(".", "p")
    if isinstance(value, dict):
        return build_parameter_signature(value)
    if isinstance(value, list):
        return "-".join(normalize_parameter_value(item) for item in value)
    return str(value)
