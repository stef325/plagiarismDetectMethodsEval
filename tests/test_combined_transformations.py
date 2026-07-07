from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from preprocessing.representation.combined_representation import CombinedRepresentation
from preprocessing.representation.harmony_representation import (
    HarmonyEvent,
    HarmonyRepresentation,
)
from preprocessing.representation.melody_representation import (
    MelodyNote,
    MelodyRepresentation,
)
from preprocessing.representation.rhythm_representation import (
    RhythmEvent,
    RhythmRepresentation,
)
from transformations.combined.harmony_rhythm import HarmonyRhythmTransformation
from transformations.combined.melody_harmony import MelodyHarmonyTransformation
from transformations.combined.melody_harmony_rhythm import (
    MelodyHarmonyRhythmTransformation,
)
from transformations.combined.melody_rhythm import MelodyRhythmTransformation


def _build_melody() -> MelodyRepresentation:
    return MelodyRepresentation(
        segment_file="001_segment_01.mid",
        notes=(
            MelodyNote(pitch=60, duration=0.5),
            MelodyNote(pitch=62, duration=0.25),
        ),
    )


def _build_harmony() -> HarmonyRepresentation:
    return HarmonyRepresentation(
        segment_file="001_segment_01.mid",
        harmony=(
            HarmonyEvent(start=0.0, end=0.5, chord="C4-E4-G4"),
            HarmonyEvent(start=0.5, end=1.0, chord="F4-A4-C5"),
        ),
    )


def _build_rhythm() -> RhythmRepresentation:
    return RhythmRepresentation(
        segment_file="001_segment_01.mid",
        rhythm=(
            RhythmEvent(onset=0.0, duration=0.5),
            RhythmEvent(onset=0.5, duration=0.25),
        ),
    )


class MelodyHarmonyTransformationTestCase(unittest.TestCase):
    def test_transform_applies_melody_and_harmony(self) -> None:
        melody = _build_melody()
        harmony = _build_harmony()
        rhythm = _build_rhythm()

        transformed_melody = MelodyRepresentation(
            segment_file=melody.segment_file,
            notes=(MelodyNote(pitch=70, duration=0.5),),
        )
        transformed_harmony = HarmonyRepresentation(
            segment_file=harmony.segment_file,
            harmony=(HarmonyEvent(start=0.0, end=0.5, chord="D4-F#4-A4"),),
        )

        with patch(
            "transformations.combined.melody_harmony.TranspositionTransformation.transform",
            return_value=transformed_melody,
        ) as mocked_melody_transform, patch(
            "transformations.combined.melody_harmony.ChordSubstitutionTransformation.transform",
            return_value=transformed_harmony,
        ) as mocked_harmony_transform:
            result = MelodyHarmonyTransformation().transform(
                melody=melody,
                harmony=harmony,
                rhythm=rhythm,
                melody_transformation="transpose",
                melody_parameters={"semitones": 2},
                harmony_transformation="chord_substitution",
                harmony_parameters={"strength": 0.25},
                random_seed=42,
            )

        self.assertIsInstance(result, CombinedRepresentation)
        self.assertEqual(result.melody, transformed_melody)
        self.assertEqual(result.harmony, transformed_harmony)
        self.assertEqual(result.rhythm, rhythm)
        mocked_melody_transform.assert_called_once()
        mocked_harmony_transform.assert_called_once()
        self.assertEqual(melody, _build_melody())
        self.assertEqual(harmony, _build_harmony())


class MelodyRhythmTransformationTestCase(unittest.TestCase):
    def test_transform_applies_melody_and_rhythm(self) -> None:
        melody = _build_melody()
        harmony = _build_harmony()
        rhythm = _build_rhythm()

        transformed_melody = MelodyRepresentation(
            segment_file=melody.segment_file,
            notes=(MelodyNote(pitch=70, duration=0.5),),
        )
        transformed_rhythm = RhythmRepresentation(
            segment_file=rhythm.segment_file,
            rhythm=(RhythmEvent(onset=0.0, duration=1.0),),
        )

        with patch(
            "transformations.combined.melody_rhythm.TranspositionTransformation.transform",
            return_value=transformed_melody,
        ) as mocked_melody_transform, patch(
            "transformations.combined.melody_rhythm.TempoChangeTransformation.transform",
            return_value=transformed_rhythm,
        ) as mocked_rhythm_transform:
            result = MelodyRhythmTransformation().transform(
                melody=melody,
                harmony=harmony,
                rhythm=rhythm,
                melody_transformation="transpose",
                melody_parameters={"semitones": 2},
                rhythm_transformation="tempo_change",
                rhythm_parameters={"tempo_factor": 0.8},
                random_seed=42,
            )

        self.assertEqual(result.melody, transformed_melody)
        self.assertEqual(result.harmony, harmony)
        self.assertEqual(result.rhythm, transformed_rhythm)
        mocked_melody_transform.assert_called_once()
        mocked_rhythm_transform.assert_called_once()


class HarmonyRhythmTransformationTestCase(unittest.TestCase):
    def test_transform_applies_harmony_and_rhythm(self) -> None:
        melody = _build_melody()
        harmony = _build_harmony()
        rhythm = _build_rhythm()

        transformed_harmony = HarmonyRepresentation(
            segment_file=harmony.segment_file,
            harmony=(HarmonyEvent(start=0.0, end=0.5, chord="D4-F#4-A4"),),
        )
        transformed_rhythm = RhythmRepresentation(
            segment_file=rhythm.segment_file,
            rhythm=(RhythmEvent(onset=0.0, duration=1.0),),
        )

        with patch(
            "transformations.combined.harmony_rhythm.ChordSubstitutionTransformation.transform",
            return_value=transformed_harmony,
        ) as mocked_harmony_transform, patch(
            "transformations.combined.harmony_rhythm.TempoChangeTransformation.transform",
            return_value=transformed_rhythm,
        ) as mocked_rhythm_transform:
            result = HarmonyRhythmTransformation().transform(
                melody=melody,
                harmony=harmony,
                rhythm=rhythm,
                harmony_transformation="chord_substitution",
                harmony_parameters={"strength": 0.25},
                rhythm_transformation="tempo_change",
                rhythm_parameters={"tempo_factor": 0.8},
                random_seed=42,
            )

        self.assertEqual(result.melody, melody)
        self.assertEqual(result.harmony, transformed_harmony)
        self.assertEqual(result.rhythm, transformed_rhythm)
        mocked_harmony_transform.assert_called_once()
        mocked_rhythm_transform.assert_called_once()


class MelodyHarmonyRhythmTransformationTestCase(unittest.TestCase):
    def test_transform_applies_all_categories(self) -> None:
        melody = _build_melody()
        harmony = _build_harmony()
        rhythm = _build_rhythm()

        transformed_melody = MelodyRepresentation(
            segment_file=melody.segment_file,
            notes=(MelodyNote(pitch=70, duration=0.5),),
        )
        transformed_harmony = HarmonyRepresentation(
            segment_file=harmony.segment_file,
            harmony=(HarmonyEvent(start=0.0, end=0.5, chord="D4-F#4-A4"),),
        )
        transformed_rhythm = RhythmRepresentation(
            segment_file=rhythm.segment_file,
            rhythm=(RhythmEvent(onset=0.0, duration=1.0),),
        )

        with patch(
            "transformations.combined.melody_harmony_rhythm.TranspositionTransformation.transform",
            return_value=transformed_melody,
        ) as mocked_melody_transform, patch(
            "transformations.combined.melody_harmony_rhythm.ChordSubstitutionTransformation.transform",
            return_value=transformed_harmony,
        ) as mocked_harmony_transform, patch(
            "transformations.combined.melody_harmony_rhythm.TempoChangeTransformation.transform",
            return_value=transformed_rhythm,
        ) as mocked_rhythm_transform:
            result = MelodyHarmonyRhythmTransformation().transform(
                melody=melody,
                harmony=harmony,
                rhythm=rhythm,
                melody_transformation="transpose",
                melody_parameters={"semitones": 2},
                harmony_transformation="chord_substitution",
                harmony_parameters={"strength": 0.25},
                rhythm_transformation="tempo_change",
                rhythm_parameters={"tempo_factor": 0.8},
                random_seed=42,
            )

        self.assertEqual(result.melody, transformed_melody)
        self.assertEqual(result.harmony, transformed_harmony)
        self.assertEqual(result.rhythm, transformed_rhythm)
        mocked_melody_transform.assert_called_once()
        mocked_harmony_transform.assert_called_once()
        mocked_rhythm_transform.assert_called_once()


if __name__ == "__main__":
    unittest.main()
