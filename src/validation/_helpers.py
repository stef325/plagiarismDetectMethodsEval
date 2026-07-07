"""Utilitários compartilhados pelos validadores."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from preprocessing.representation.combined_representation import CombinedRepresentation
from preprocessing.representation.harmony_representation import HarmonyRepresentation
from preprocessing.representation.melody_representation import MelodyRepresentation
from preprocessing.representation.rhythm_representation import RhythmRepresentation


MELODY_TRANSFORMATIONS = {
    "transpose": ("semitones",),
    "interval_modification": ("strength",),
    "ornamentation": ("density",),
    "simplification": ("strength",),
}

HARMONY_TRANSFORMATIONS = {
    "chord_substitution": ("strength",),
    "reharmonization": ("strength",),
    "simplification": ("strength",),
}

RHYTHM_TRANSFORMATIONS = {
    "tempo_change": ("tempo_factor",),
    "duration_scaling": ("duration_factor",),
    "partial_rhythm_modification": ("strength",),
}

COMBINED_COMPONENTS = {
    "melody_harmony": ("melody", "harmony"),
    "melody_rhythm": ("melody", "rhythm"),
    "harmony_rhythm": ("harmony", "rhythm"),
    "melody_harmony_rhythm": ("melody", "harmony", "rhythm"),
}


def load_json(path: Path) -> dict[str, Any]:
    """Carrega um JSON do disco."""

    import json

    return json.loads(path.read_text(encoding="utf-8"))


def load_combined_representation(path: Path) -> CombinedRepresentation:
    """Carrega uma representação musical completa."""

    return CombinedRepresentation.from_dict(load_json(path))


def load_melody_representation(path: Path) -> MelodyRepresentation:
    """Carrega uma representação melódica."""

    return MelodyRepresentation.from_dict(load_json(path))


def load_harmony_representation(path: Path) -> HarmonyRepresentation:
    """Carrega uma representação harmônica."""

    return HarmonyRepresentation.from_dict(load_json(path))


def load_rhythm_representation(path: Path) -> RhythmRepresentation:
    """Carrega uma representação rítmica."""

    return RhythmRepresentation.from_dict(load_json(path))


def parse_segment_identifier(segment_file: str) -> tuple[str, str]:
    """Extrai song_id e segment_id do nome do segmento."""

    stem = Path(segment_file).stem
    parts = stem.split("_segment_")
    if len(parts) != 2:
        return stem, stem
    return parts[0], parts[1]


def parse_parameters(metadata: dict[str, Any]) -> dict[str, Any]:
    """Normaliza os parâmetros vindos dos metadados."""

    raw_parameters = metadata.get("parameters", {})
    if isinstance(raw_parameters, dict):
        return raw_parameters
    if isinstance(raw_parameters, str) and raw_parameters:
        import json

        loaded = json.loads(raw_parameters)
        if isinstance(loaded, dict):
            return loaded
    return {}


def expected_components_for_combination(combination: str) -> tuple[str, ...]:
    """Retorna os componentes esperados como alterados em uma combinação."""

    return COMBINED_COMPONENTS[combination]


def preserved_components_for_combination(combination: str) -> tuple[str, ...]:
    """Retorna os componentes esperados como preservados em uma combinação."""

    all_components = ("melody", "harmony", "rhythm")
    changed = set(expected_components_for_combination(combination))
    return tuple(component for component in all_components if component not in changed)
