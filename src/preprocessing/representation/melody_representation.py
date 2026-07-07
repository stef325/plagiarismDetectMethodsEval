"""Modelo imutável para representacoes melodicas."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MelodyNote:
    """Representa uma nota melodica em pitch e duracao."""

    pitch: int
    duration: float


@dataclass(frozen=True)
class MelodyRepresentation:
    """Representa uma melodia extraida de um segmento."""

    segment_file: str
    notes: tuple[MelodyNote, ...]

    def to_dict(self) -> dict[str, object]:
        """Converte a representacao para um dicionario serializavel."""

        return {
            "segment_file": self.segment_file,
            "melody": [
                {"pitch": note.pitch, "duration": note.duration}
                for note in self.notes
            ],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "MelodyRepresentation":
        """Cria a representacao a partir de um payload JSON."""

        segment_file = str(payload["segment_file"])
        melody_payload = payload.get("melody", [])
        notes = tuple(
            MelodyNote(
                pitch=int(note_payload["pitch"]),
                duration=float(note_payload["duration"]),
            )
            for note_payload in melody_payload
            if isinstance(note_payload, dict)
        )
        return cls(segment_file=segment_file, notes=notes)
