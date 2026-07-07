"""Transformacao de modificacao de intervalos melodicos."""

from __future__ import annotations

import random

from preprocessing.representation.melody_representation import (
    MelodyNote,
    MelodyRepresentation,
)


class IntervalModificationTransformation:
    """Modifica intervalos entre notas preservando o contorno geral."""

    def transform(
        self,
        representation: MelodyRepresentation,
        strength: float,
        random_seed: int,
    ) -> MelodyRepresentation:
        """Altera uma porcentagem dos intervalos entre notas."""

        if not representation.notes or len(representation.notes) < 2 or strength <= 0:
            return MelodyRepresentation(
                segment_file=representation.segment_file,
                notes=representation.notes,
            )

        notes = list(representation.notes)
        boundaries = list(range(len(notes) - 1))
        modifications = min(len(boundaries), max(1, round(len(boundaries) * strength)))
        rng = random.Random(random_seed)
        selected_boundaries = set(rng.sample(boundaries, modifications))

        transformed_notes: list[MelodyNote] = []
        pitch_offset = 0

        for index, note in enumerate(notes):
            transformed_notes.append(
                MelodyNote(
                    pitch=self._clamp_pitch(note.pitch + pitch_offset),
                    duration=note.duration,
                )
            )

            if index in selected_boundaries:
                interval = notes[index + 1].pitch - note.pitch
                pitch_offset += self._build_delta(interval, rng)

        return MelodyRepresentation(
            segment_file=representation.segment_file,
            notes=tuple(transformed_notes),
        )

    def _build_delta(self, interval: int, rng: random.Random) -> int:
        """Gera um deslocamento pequeno preservando a direcao do intervalo."""

        step = rng.choice([1, 2])
        if interval > 0:
            return step
        if interval < 0:
            return -step
        return rng.choice([-step, step])

    def _clamp_pitch(self, pitch: int) -> int:
        """Mantem o pitch dentro do intervalo MIDI valido."""

        return max(0, min(127, pitch))
