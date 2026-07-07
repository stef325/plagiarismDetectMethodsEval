"""Extrai representacao ritmica a partir de um MIDI segmentado."""

from __future__ import annotations

import pretty_midi


class RhythmExtractor:
    """Extrai o padrao ritmico de um arquivo MIDI."""

    def extract(self, midi: pretty_midi.PrettyMIDI) -> list[dict[str, float]]:
        """Extrai pares onset-duration de todas as notas."""

        rhythm_events: list[dict[str, float]] = []

        for instrument in midi.instruments:
            if instrument.is_drum:
                continue

            for note in instrument.notes:
                rhythm_events.append(
                    {
                        "onset": round(note.start, 6),
                        "duration": round(note.end - note.start, 6),
                    }
                )

        return sorted(rhythm_events, key=lambda event: (event["onset"], event["duration"]))
