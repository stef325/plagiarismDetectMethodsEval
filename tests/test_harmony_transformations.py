from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from preprocessing.representation.harmony_representation import (
    HarmonyEvent,
    HarmonyRepresentation,
)
from transformations.harmony.chord_substitution import (
    ChordSubstitutionTransformation,
)
from transformations.harmony.reharmonization import ReharmonizationTransformation
from transformations.harmony.simplification import SimplificationTransformation


def _build_representation() -> HarmonyRepresentation:
    return HarmonyRepresentation(
        segment_file="001_segment_01.mid",
        harmony=(
            HarmonyEvent(start=0.0, end=0.5, chord="C4-E4-G4"),
            HarmonyEvent(start=0.5, end=1.0, chord="F4-A4-C5"),
            HarmonyEvent(start=1.0, end=1.5, chord="G4-B4-D5"),
            HarmonyEvent(start=1.5, end=2.0, chord="Cmaj7"),
        ),
    )


class ChordSubstitutionTransformationTestCase(unittest.TestCase):
    def test_transform_substitutes_some_chords(self) -> None:
        representation = _build_representation()

        transformed = ChordSubstitutionTransformation().transform(
            representation,
            strength=0.5,
            random_seed=42,
        )

        self.assertEqual(len(transformed.harmony), len(representation.harmony))
        self.assertNotEqual(transformed.harmony, representation.harmony)
        self.assertEqual(representation, _build_representation())


class ReharmonizationTransformationTestCase(unittest.TestCase):
    def test_transform_reharmonizes_contiguous_span(self) -> None:
        representation = _build_representation()

        transformed = ReharmonizationTransformation().transform(
            representation,
            strength=0.5,
            random_seed=42,
        )

        self.assertEqual(len(transformed.harmony), len(representation.harmony))
        self.assertNotEqual(transformed.harmony, representation.harmony)
        self.assertEqual(representation, _build_representation())


class SimplificationTransformationTestCase(unittest.TestCase):
    def test_transform_simplifies_complex_chords(self) -> None:
        representation = _build_representation()

        transformed = SimplificationTransformation().transform(
            representation,
            strength=0.75,
            random_seed=42,
        )

        self.assertEqual(len(transformed.harmony), len(representation.harmony))
        self.assertTrue(
            any(
                event.chord != original.chord
                for event, original in zip(transformed.harmony, representation.harmony)
            )
        )
        self.assertEqual(representation, _build_representation())


if __name__ == "__main__":
    unittest.main()