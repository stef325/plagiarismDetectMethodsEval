from __future__ import annotations

from importlib import import_module
from pathlib import Path

from preprocessing.representation.harmony_representation import HarmonyRepresentation
from preprocessing.representation.melody_representation import MelodyRepresentation
from preprocessing.representation.rhythm_representation import RhythmRepresentation


def build_melody_representation(pitches: list[int], durations: list[float] | None = None) -> MelodyRepresentation:
    """Cria uma representação melódica artificial para testes."""

    if durations is None:
        durations = [0.5] * len(pitches)
    return MelodyRepresentation.from_dict(
        {
            "segment_file": "001_segment_01.mid",
            "melody": [
                {"pitch": pitch, "duration": duration}
                for pitch, duration in zip(pitches, durations, strict=True)
            ],
        }
    )


def build_harmony_representation(chords: list[str]) -> HarmonyRepresentation:
    """Cria uma representação harmônica artificial para testes."""

    return HarmonyRepresentation.from_dict(
        {
            "segment_file": "001_segment_01.mid",
            "harmony": [
                {"start": float(index), "end": float(index + 1), "chord": chord}
                for index, chord in enumerate(chords)
            ],
        }
    )


def build_rhythm_representation(events: list[tuple[float, float]]) -> RhythmRepresentation:
    """Cria uma representação rítmica artificial para testes."""

    return RhythmRepresentation.from_dict(
        {
            "segment_file": "001_segment_01.mid",
            "rhythm": [
                {"onset": onset, "duration": duration}
                for onset, duration in events
            ],
        }
    )


def build_global_metric_module() -> object:
    """Carrega o pacote de métricas globais."""

    return import_module("metrics.global")


def record_metric_value(request, value: float) -> None:
    """Registra o valor calculado para uso no relatório do pipeline."""

    request.node.user_properties.append(("metric_value", f"{value:.6f}"))

