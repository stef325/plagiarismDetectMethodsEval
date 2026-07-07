"""Transformação de simplificação harmônica."""

from __future__ import annotations

import random

from preprocessing.representation.harmony_representation import (
    HarmonyEvent,
    HarmonyRepresentation,
)

from ._helpers import simplify_chord_label


class SimplificationTransformation:
    """Reduz a complexidade da progressão harmônica."""

    def transform(
        self,
        representation: HarmonyRepresentation,
        strength: float,
        random_seed: int | None = None,
    ) -> HarmonyRepresentation:
        """Simplifica uma porcentagem dos acordes da representação."""

        if not representation.harmony or strength <= 0:
            return HarmonyRepresentation(
                segment_file=representation.segment_file,
                harmony=representation.harmony,
            )

        rng = random.Random(random_seed)
        events = list(representation.harmony)
        simplification_count = min(len(events), max(1, round(len(events) * strength)))
        selected_indices = set(rng.sample(range(len(events)), simplification_count))

        transformed_events = tuple(
            HarmonyEvent(
                start=event.start,
                end=event.end,
                chord=simplify_chord_label(event.chord)
                if index in selected_indices
                else event.chord,
            )
            for index, event in enumerate(events)
        )
        return HarmonyRepresentation(
            segment_file=representation.segment_file,
            harmony=transformed_events,
        )