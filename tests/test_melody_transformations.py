from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from preprocessing.representation.melody_representation import (
    MelodyNote,
    MelodyRepresentation,
)
from transformations.melody.interval_modification import (
    IntervalModificationTransformation,
)
from transformations.melody.ornamentation import OrnamentationTransformation
from transformations.melody.simplification import SimplificationTransformation
from transformations.melody.transpose import TranspositionTransformation


def _build_representation() -> MelodyRepresentation:
    return MelodyRepresentation(
        segment_file="001_segment_01.mid",
        notes=(
            MelodyNote(pitch=60, duration=0.5),
            MelodyNote(pitch=62, duration=0.25),
            MelodyNote(pitch=64, duration=0.5),
            MelodyNote(pitch=65, duration=0.25),
        ),
    )


class TranspositionTransformationTestCase(unittest.TestCase):
    def test_transform_shifts_all_pitches(self) -> None:
        representation = _build_representation()
        original_notes = representation.notes

        transformed = TranspositionTransformation().transform(representation, 2)

        self.assertEqual(
            transformed.notes,
            (
                MelodyNote(pitch=62, duration=0.5),
                MelodyNote(pitch=64, duration=0.25),
                MelodyNote(pitch=66, duration=0.5),
                MelodyNote(pitch=67, duration=0.25),
            ),
        )
        self.assertEqual(representation.notes, original_notes)


class IntervalModificationTransformationTestCase(unittest.TestCase):
    def test_transform_changes_intervals_without_changing_durations(self) -> None:
        representation = _build_representation()

        transformed = IntervalModificationTransformation().transform(
            representation,
            strength=0.5,
            random_seed=42,
        )

        self.assertEqual(len(transformed.notes), len(representation.notes))
        self.assertEqual(
            [note.duration for note in transformed.notes],
            [note.duration for note in representation.notes],
        )
        self.assertNotEqual(transformed.notes, representation.notes)
        self.assertEqual(representation, _build_representation())


class OrnamentationTransformationTestCase(unittest.TestCase):
    def test_transform_inserts_ornamental_notes(self) -> None:
        representation = _build_representation()

        transformed = OrnamentationTransformation().transform(
            representation,
            density=0.5,
            random_seed=42,
        )

        self.assertGreater(len(transformed.notes), len(representation.notes))
        self.assertEqual(representation, _build_representation())
        original_pitches = [note.pitch for note in representation.notes]
        transformed_originals = [note.pitch for note in transformed.notes if note.pitch in original_pitches]
        self.assertGreaterEqual(len(transformed_originals), len(original_pitches))


class SimplificationTransformationTestCase(unittest.TestCase):
    def test_transform_removes_short_notes(self) -> None:
        representation = _build_representation()

        transformed = SimplificationTransformation().transform(
            representation,
            strength=0.5,
            random_seed=42,
        )

        self.assertLess(len(transformed.notes), len(representation.notes))
        self.assertEqual(transformed.notes[0], representation.notes[0])
        self.assertEqual(transformed.notes[-1], representation.notes[-1])
        self.assertEqual(representation, _build_representation())


if __name__ == "__main__":
    unittest.main()
