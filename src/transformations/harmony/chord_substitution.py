"""Transformação de substituição de acordes."""

from __future__ import annotations

import random

from preprocessing.representation.harmony_representation import (
    HarmonyEvent,
    HarmonyRepresentation,
)

from ._helpers import transpose_chord_label


class ChordSubstitutionTransformation:
    """Substitui parte dos acordes por alternativas funcionalmente próximas."""

    def transform(
        self,
        representation: HarmonyRepresentation,
        strength: float,
        random_seed: int,
    ) -> HarmonyRepresentation:
        """Substitui uma porcentagem dos acordes preservando a estrutura geral."""

        if not representation.harmony or strength <= 0:
            return HarmonyRepresentation(
                segment_file=representation.segment_file,
                harmony=representation.harmony,
            )

        rng = random.Random(random_seed)
        events = list(representation.harmony)
        substitution_count = min(len(events), max(1, round(len(events) * strength)))
        selected_indices = set(rng.sample(range(len(events)), substitution_count))

        transformed_events = tuple(
            HarmonyEvent(
                start=event.start,
                end=event.end,
                chord=self._substitute_chord(event.chord, rng)
                if index in selected_indices
                else event.chord,
            )
            for index, event in enumerate(events)
        )
        return HarmonyRepresentation(
            segment_file=representation.segment_file,
            harmony=transformed_events,
        )

    def _substitute_chord(self, chord: str, rng: random.Random) -> str:
        """Seleciona uma substituição próxima para um acorde."""

        intervals = self._candidate_intervals(chord)
        interval = rng.choice(intervals)
        substituted = transpose_chord_label(chord, interval)
        if substituted == chord and len(intervals) > 1:
            remaining = [candidate for candidate in intervals if candidate != interval]
            substituted = transpose_chord_label(chord, rng.choice(remaining))
        return substituted

    def _candidate_intervals(self, chord: str) -> list[int]:
        """Define intervalos de substituição plausíveis para o acorde."""

        lowered = chord.lower()
        if "dim" in lowered:
            return [1, 3, 6]
        if "aug" in lowered:
            return [1, 4, 8]
        if "maj" in lowered:
            return [-3, 4, 7]
        if "m" in lowered and "maj" not in lowered:
            return [3, 5, 7]
        if "7" in lowered:
            return [-3, 4, 7]
        return [-3, 3, 5, 7]