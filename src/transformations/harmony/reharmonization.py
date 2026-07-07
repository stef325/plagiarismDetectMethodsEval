"""Transformação de reharmonização."""

from __future__ import annotations

import random

from preprocessing.representation.harmony_representation import (
    HarmonyEvent,
    HarmonyRepresentation,
)

from ._helpers import transpose_chord_label


class ReharmonizationTransformation:
    """Altera trechos da progressão harmônica preservando a quantidade de eventos."""

    def transform(
        self,
        representation: HarmonyRepresentation,
        strength: float,
        random_seed: int,
    ) -> HarmonyRepresentation:
        """Reharmoniza uma parte da progressão de forma reprodutível."""

        if not representation.harmony or strength <= 0:
            return HarmonyRepresentation(
                segment_file=representation.segment_file,
                harmony=representation.harmony,
            )

        events = list(representation.harmony)
        window_size = min(len(events), max(1, round(len(events) * strength)))
        rng = random.Random(random_seed)
        start_index = rng.randrange(0, len(events) - window_size + 1)
        end_index = start_index + window_size

        transformed_events: list[HarmonyEvent] = []
        for index, event in enumerate(events):
            if start_index <= index < end_index:
                interval = self._reharmonization_interval(index - start_index, rng)
                transformed_events.append(
                    HarmonyEvent(
                        start=event.start,
                        end=event.end,
                        chord=transpose_chord_label(event.chord, interval),
                    )
                )
            else:
                transformed_events.append(event)

        return HarmonyRepresentation(
            segment_file=representation.segment_file,
            harmony=tuple(transformed_events),
        )

    def _reharmonization_interval(self, position: int, rng: random.Random) -> int:
        """Seleciona um intervalo harmônico simples para a reharmonização."""

        progression = [5, 7, 2, -3]
        base_interval = progression[position % len(progression)]
        variation = rng.choice([0, 1, -1])
        return base_interval + variation