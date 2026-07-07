"""Transformacao de simplificacao melodica."""

from __future__ import annotations

import random

from preprocessing.representation.melody_representation import (
    MelodyRepresentation,
)


class SimplificationTransformation:
    """Remove notas de passagem ou ornamentais sem alterar a estrutura base."""

    def transform(
        self,
        representation: MelodyRepresentation,
        strength: float,
        random_seed: int | None = None,
    ) -> MelodyRepresentation:
        """Simplifica a melodia removendo notas de menor duracao."""

        if not representation.notes or len(representation.notes) <= 2 or strength <= 0:
            return MelodyRepresentation(
                segment_file=representation.segment_file,
                notes=representation.notes,
            )

        notes = list(representation.notes)
        removable_indices = list(range(1, len(notes) - 1))
        notes_to_remove = min(
            len(removable_indices),
            max(1, round(len(notes) * strength)),
        )

        ordered_candidates = removable_indices[:]
        if random_seed is not None:
            rng = random.Random(random_seed)
            rng.shuffle(ordered_candidates)

        ordered_candidates.sort(key=lambda index: (notes[index].duration, index))

        indices_to_remove = set(ordered_candidates[:notes_to_remove])
        simplified_notes = tuple(
            note for index, note in enumerate(notes) if index not in indices_to_remove
        )

        if len(simplified_notes) < 2:
            return MelodyRepresentation(
                segment_file=representation.segment_file,
                notes=representation.notes,
            )

        return MelodyRepresentation(
            segment_file=representation.segment_file,
            notes=simplified_notes,
        )
