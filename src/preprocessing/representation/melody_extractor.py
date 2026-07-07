"""Extrai representacao melodica a partir de um MIDI segmentado."""

from __future__ import annotations

from dataclasses import dataclass

import pretty_midi


@dataclass(frozen=True)
class MelodyEvent:
    """Representa uma nota melódica em termos de pitch e duracao."""

    pitch: int
    duration: float


class MelodyExtractor:
    """Extrai a representacao melodica de um arquivo MIDI."""

    def extract(self, midi: pretty_midi.PrettyMIDI) -> list[dict[str, int | float]]:
        """Extrai pitch e duration da linha principal da melodia."""

        melody_events: list[MelodyEvent] = []
        melody_notes = self._get_melody_notes(midi)

        for note in melody_notes:
            melody_events.append(
                MelodyEvent(
                    pitch=note.pitch,
                    duration=round(note.end - note.start, 6),
                )
            )

        return [
            {"pitch": event.pitch, "duration": event.duration}
            for event in melody_events
        ]

    def _get_melody_notes(
        self,
        midi: pretty_midi.PrettyMIDI,
    ) -> list[pretty_midi.Note]:
        """Seleciona uma nota por onset, priorizando o pitch mais agudo."""

        candidate_notes = [
            note
            for instrument in midi.instruments
            if not instrument.is_drum
            for note in instrument.notes
        ]
        notes_by_onset: dict[float, pretty_midi.Note] = {}

        for note in sorted(
            candidate_notes,
            key=lambda current: (round(current.start, 6), -current.pitch),
        ):
            note_onset = round(note.start, 6)
            existing_note = notes_by_onset.get(note_onset)
            if existing_note is None or note.pitch > existing_note.pitch:
                notes_by_onset[note_onset] = note

        return [notes_by_onset[start] for start in sorted(notes_by_onset)]
