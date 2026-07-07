"""Modelo imutável para representações musicais combinadas."""

from __future__ import annotations

from dataclasses import dataclass

from .harmony_representation import HarmonyRepresentation
from .melody_representation import MelodyRepresentation
from .rhythm_representation import RhythmRepresentation


@dataclass(frozen=True)
class CombinedRepresentation:
    """Representa uma combinação de melodia, harmonia e ritmo."""

    segment_file: str
    melody: MelodyRepresentation
    harmony: HarmonyRepresentation
    rhythm: RhythmRepresentation

    def to_dict(self) -> dict[str, object]:
        """Converte a representação para um dicionário serializável."""

        return {
            "segment_file": self.segment_file,
            "melody": [
                {"pitch": note.pitch, "duration": note.duration}
                for note in self.melody.notes
            ],
            "harmony": [
                {"start": event.start, "end": event.end, "chord": event.chord}
                for event in self.harmony.harmony
            ],
            "rhythm": [
                {"onset": event.onset, "duration": event.duration}
                for event in self.rhythm.rhythm
            ],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "CombinedRepresentation":
        """Cria a representação a partir de um payload JSON."""

        segment_file = str(payload["segment_file"])
        melody = MelodyRepresentation.from_dict(
            {"segment_file": segment_file, "melody": payload.get("melody", [])}
        )
        harmony = HarmonyRepresentation.from_dict(
            {"segment_file": segment_file, "harmony": payload.get("harmony", [])}
        )
        rhythm = RhythmRepresentation.from_dict(
            {"segment_file": segment_file, "rhythm": payload.get("rhythm", [])}
        )
        return cls(
            segment_file=segment_file,
            melody=melody,
            harmony=harmony,
            rhythm=rhythm,
        )
