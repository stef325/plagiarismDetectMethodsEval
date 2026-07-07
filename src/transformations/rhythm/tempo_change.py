"""Transformação de alteração de andamento."""

from __future__ import annotations

from preprocessing.representation.rhythm_representation import (
    RhythmEvent,
    RhythmRepresentation,
)


class TempoChangeTransformation:
    """Altera proporcionalmente o padrão temporal da representação."""

    def transform(
        self,
        representation: RhythmRepresentation,
        tempo_factor: float,
    ) -> RhythmRepresentation:
        """Escala onsets e durações sem alterar a quantidade de eventos."""

        if tempo_factor <= 0:
            raise ValueError("O fator de andamento deve ser positivo.")

        transformed_events = tuple(
            RhythmEvent(
                onset=round(event.onset * tempo_factor, 6),
                duration=round(event.duration * tempo_factor, 6),
            )
            for event in representation.rhythm
        )
        return RhythmRepresentation(
            segment_file=representation.segment_file,
            rhythm=transformed_events,
        )
