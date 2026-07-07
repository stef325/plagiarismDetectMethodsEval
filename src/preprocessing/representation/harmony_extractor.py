"""Extrai representacao harmonica a partir de um MIDI segmentado."""

from __future__ import annotations

import pretty_midi


class HarmonyExtractor:
    """Extrai a representacao harmonica de um arquivo MIDI."""

    def extract(self, midi: pretty_midi.PrettyMIDI) -> list[dict[str, float | str]]:
        """Extrai acordes simples do MIDI como intervalos temporais e nomes."""

        notes_by_onset: dict[float, list[pretty_midi.Note]] = {}
        for instrument in midi.instruments:
            if instrument.is_drum:
                continue
            for note in instrument.notes:
                notes_by_onset.setdefault(round(note.start, 6), []).append(note)

        events: list[dict[str, float | str]] = []
        for onset in sorted(notes_by_onset):
            grouped_notes = notes_by_onset[onset]
            chord_name = "-".join(
                pretty_midi.note_number_to_name(note.pitch)
                for note in sorted(grouped_notes, key=lambda current: current.pitch)
            )
            events.append(
                {
                    "start": round(onset, 6),
                    "end": round(max(note.end for note in grouped_notes), 6),
                    "chord": chord_name,
                }
            )

        return events
