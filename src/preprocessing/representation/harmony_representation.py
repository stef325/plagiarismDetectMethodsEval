"""Modelo imutável para representações harmônicas."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HarmonyEvent:
    """Representa um evento harmônico com intervalo temporal e acorde."""

    start: float
    end: float
    chord: str


@dataclass(frozen=True)
class HarmonyRepresentation:
    """Representa a harmonia extraída de um segmento."""

    segment_file: str
    harmony: tuple[HarmonyEvent, ...]

    def to_dict(self) -> dict[str, object]:
        """Converte a representação para um dicionário serializável."""

        return {
            "segment_file": self.segment_file,
            "harmony": [
                {"start": event.start, "end": event.end, "chord": event.chord}
                for event in self.harmony
            ],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "HarmonyRepresentation":
        """Cria a representação a partir de um payload JSON."""

        segment_file = str(payload["segment_file"])
        harmony_payload = payload.get("harmony", [])
        events = tuple(
            HarmonyEvent(
                start=float(event_payload["start"]),
                end=float(event_payload["end"]),
                chord=str(event_payload["chord"]),
            )
            for event_payload in harmony_payload
            if isinstance(event_payload, dict)
        )
        return cls(segment_file=segment_file, harmony=events)