from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from preprocessing.representation.rhythm_representation import (
    RhythmEvent,
    RhythmRepresentation,
)
from transformations.rhythm.duration_scaling import DurationScalingTransformation
from transformations.rhythm.partial_rhythm_modification import (
    PartialRhythmModificationTransformation,
)
from transformations.rhythm.tempo_change import TempoChangeTransformation


def _build_representation() -> RhythmRepresentation:
    return RhythmRepresentation(
        segment_file="001_segment_01.mid",
        rhythm=(
            RhythmEvent(onset=0.0, duration=0.5),
            RhythmEvent(onset=0.5, duration=0.25),
            RhythmEvent(onset=0.75, duration=0.5),
            RhythmEvent(onset=1.25, duration=0.25),
        ),
    )


class TempoChangeTransformationTestCase(unittest.TestCase):
    def test_transform_scales_onsets_and_durations(self) -> None:
        representation = _build_representation()

        transformed = TempoChangeTransformation().transform(
            representation,
            tempo_factor=0.8,
        )

        self.assertEqual(
            transformed.rhythm[0],
            RhythmEvent(onset=0.0, duration=0.4),
        )
        self.assertEqual(representation, _build_representation())


class DurationScalingTransformationTestCase(unittest.TestCase):
    def test_transform_scales_durations_and_recomputes_onsets(self) -> None:
        representation = _build_representation()

        transformed = DurationScalingTransformation().transform(
            representation,
            duration_factor=1.2,
        )

        self.assertEqual(transformed.rhythm[0].duration, 0.6)
        self.assertGreaterEqual(transformed.rhythm[1].onset, transformed.rhythm[0].onset)
        self.assertEqual(representation, _build_representation())


class PartialRhythmModificationTransformationTestCase(unittest.TestCase):
    def test_transform_modifies_part_of_the_pattern(self) -> None:
        representation = _build_representation()

        transformed = PartialRhythmModificationTransformation().transform(
            representation,
            strength=0.5,
            random_seed=42,
        )

        self.assertEqual(len(transformed.rhythm), len(representation.rhythm))
        self.assertNotEqual(transformed.rhythm, representation.rhythm)
        self.assertEqual(representation, _build_representation())


if __name__ == "__main__":
    unittest.main()
