"""Transformacao de transposicao melodica."""

from __future__ import annotations

from preprocessing.representation.melody_representation import (
    MelodyNote,
    MelodyRepresentation,
)


class TranspositionTransformation:
    """Aplica uma transposicao em semitons na melodia."""

    def transform(
        self,
        representation: MelodyRepresentation,
        semitones: int,
    ) -> MelodyRepresentation:
        """Transpoe todos os pitches sem alterar duracao ou ordem."""

        transposed_notes = tuple(
            MelodyNote(
                pitch=self._clamp_pitch(note.pitch + semitones),
                duration=note.duration,
            )
            for note in representation.notes
        )
        return MelodyRepresentation(
            segment_file=representation.segment_file,
            notes=transposed_notes,
        )

    def _clamp_pitch(self, pitch: int) -> int:
        """Mantem o pitch dentro do intervalo MIDI valido."""

        return max(0, min(127, pitch))
