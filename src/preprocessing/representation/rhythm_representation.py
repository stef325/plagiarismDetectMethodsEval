"""Modelo imutável para representações rítmicas."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RhythmEvent:
    """Representa um evento rítmico com onset e duração."""

    onset: float
    duration: float


@dataclass(frozen=True)
class RhythmRepresentation:
    """Representa o padrão rítmico extraído de um segmento."""

    segment_file: str
    rhythm: tuple[RhythmEvent, ...]

    def to_dict(self) -> dict[str, object]:
        """Converte a representação para um dicionário serializável."""

        return {
            "segment_file": self.segment_file,
            "rhythm": [
                {"onset": event.onset, "duration": event.duration}
                for event in self.rhythm
            ],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "RhythmRepresentation":
        """Cria a representação a partir de um payload JSON."""

        segment_file = str(payload["segment_file"])
        rhythm_payload = payload.get("rhythm", [])
        events = tuple(
            RhythmEvent(
                onset=float(event_payload["onset"]),
                duration=float(event_payload["duration"]),
            )
            for event_payload in rhythm_payload
            if isinstance(event_payload, dict)
        )
        return cls(segment_file=segment_file, rhythm=events)
