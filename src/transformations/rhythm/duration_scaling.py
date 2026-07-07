"""Transformação de escalonamento de durações."""

from __future__ import annotations

from preprocessing.representation.rhythm_representation import (
    RhythmEvent,
    RhythmRepresentation,
)


class DurationScalingTransformation:
    """Altera apenas as durações, mantendo a coerência dos onsets."""

    def transform(
        self,
        representation: RhythmRepresentation,
        duration_factor: float,
    ) -> RhythmRepresentation:
        """Escala as durações e recompõe os onsets de forma coerente."""

        if duration_factor <= 0:
            raise ValueError("O fator de duração deve ser positivo.")

        events = list(representation.rhythm)
        if not events:
            return RhythmRepresentation(
                segment_file=representation.segment_file,
                rhythm=representation.rhythm,
            )

        transformed_events: list[RhythmEvent] = []
        current_onset = events[0].onset
        for index, event in enumerate(events):
            scaled_duration = round(event.duration * duration_factor, 6)
            transformed_events.append(
                RhythmEvent(
                    onset=round(current_onset, 6),
                    duration=scaled_duration,
                )
            )
            current_onset = current_onset + scaled_duration

            if index + 1 < len(events):
                next_original_gap = max(0.0, events[index + 1].onset - event.onset - event.duration)
                current_onset = current_onset + round(next_original_gap, 6)

        return RhythmRepresentation(
            segment_file=representation.segment_file,
            rhythm=tuple(transformed_events),
        )
