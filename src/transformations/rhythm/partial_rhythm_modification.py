"""Transformação de alteração parcial do ritmo."""

from __future__ import annotations

import random

from preprocessing.representation.rhythm_representation import (
    RhythmEvent,
    RhythmRepresentation,
)


class PartialRhythmModificationTransformation:
    """Modifica uma porcentagem dos eventos rítmicos de forma reprodutível."""

    def transform(
        self,
        representation: RhythmRepresentation,
        strength: float,
        random_seed: int,
    ) -> RhythmRepresentation:
        """Altera apenas parte dos eventos mantendo a estrutura geral."""

        events = list(representation.rhythm)
        if not events or strength <= 0:
            return RhythmRepresentation(
                segment_file=representation.segment_file,
                rhythm=representation.rhythm,
            )

        rng = random.Random(random_seed)
        modification_count = min(len(events), max(1, round(len(events) * strength)))
        selected_indices = set(rng.sample(range(len(events)), modification_count))

        transformed_events: list[RhythmEvent] = []

        for index, event in enumerate(events):
            if index in selected_indices:
                factor = rng.choice([0.75, 0.85, 1.15, 1.25])
                modified_duration = round(event.duration * factor, 6)
            else:
                modified_duration = event.duration

            if index == 0:
                transformed_onset = event.onset
            else:
                previous_end = transformed_events[-1].onset + transformed_events[-1].duration
                transformed_onset = round(max(event.onset, previous_end), 6)
            transformed_events.append(
                RhythmEvent(
                    onset=transformed_onset,
                    duration=round(modified_duration, 6),
                )
            )

        return RhythmRepresentation(
            segment_file=representation.segment_file,
            rhythm=tuple(transformed_events),
        )
