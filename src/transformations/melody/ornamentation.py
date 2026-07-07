"""Transformacao de ornamentacao melodica."""

from __future__ import annotations

import random

from preprocessing.representation.melody_representation import (
    MelodyNote,
    MelodyRepresentation,
)


class OrnamentationTransformation:
    """Insere notas ornamentais sem remover a melodia original."""

    def transform(
        self,
        representation: MelodyRepresentation,
        density: float,
        random_seed: int,
    ) -> MelodyRepresentation:
        """Insere notas ornamentais entre notas existentes."""

        if not representation.notes or len(representation.notes) < 2 or density <= 0:
            return MelodyRepresentation(
                segment_file=representation.segment_file,
                notes=representation.notes,
            )

        notes = list(representation.notes)
        insertion_points = list(range(len(notes) - 1))
        ornaments_to_add = min(
            len(insertion_points),
            max(1, round(len(insertion_points) * density)),
        )
        rng = random.Random(random_seed)
        selected_points = set(rng.sample(insertion_points, ornaments_to_add))

        transformed_notes: list[MelodyNote] = []

        for index, note in enumerate(notes):
            transformed_notes.append(note)
            if index in selected_points:
                transformed_notes.append(
                    self._build_ornament(note, notes[index + 1], rng)
                )

        return MelodyRepresentation(
            segment_file=representation.segment_file,
            notes=tuple(transformed_notes),
        )

    def _build_ornament(
        self,
        current_note: MelodyNote,
        next_note: MelodyNote,
        rng: random.Random,
    ) -> MelodyNote:
        """Cria uma nota ornamental curta entre duas notas existentes."""

        midpoint = round((current_note.pitch + next_note.pitch) / 2)
        pitch_shift = rng.choice([-1, 1])
        duration = max(min(current_note.duration, next_note.duration) / 2, 0.125)
        return MelodyNote(
            pitch=self._clamp_pitch(midpoint + pitch_shift),
            duration=round(duration, 6),
        )

    def _clamp_pitch(self, pitch: int) -> int:
        """Mantem o pitch dentro do intervalo MIDI valido."""

        return max(0, min(127, pitch))
