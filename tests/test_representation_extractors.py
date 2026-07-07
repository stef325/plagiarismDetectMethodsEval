from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pretty_midi

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from preprocessing.representation.harmony_extractor import HarmonyExtractor
from preprocessing.representation.melody_extractor import MelodyExtractor
from preprocessing.representation.rhythm_extractor import RhythmExtractor


def _build_polyphonic_midi() -> pretty_midi.PrettyMIDI:
    midi = pretty_midi.PrettyMIDI(initial_tempo=120)

    melody = pretty_midi.Instrument(program=0)
    melody.notes.extend(
        [
            pretty_midi.Note(velocity=100, pitch=60, start=0.0, end=0.5),
            pretty_midi.Note(velocity=100, pitch=64, start=0.0, end=0.25),
            pretty_midi.Note(velocity=100, pitch=67, start=1.0, end=1.5),
        ]
    )

    harmony = pretty_midi.Instrument(program=1)
    harmony.notes.extend(
        [
            pretty_midi.Note(velocity=100, pitch=48, start=0.0, end=1.0),
            pretty_midi.Note(velocity=100, pitch=52, start=0.0, end=1.0),
            pretty_midi.Note(velocity=100, pitch=55, start=0.0, end=1.0),
            pretty_midi.Note(velocity=100, pitch=50, start=1.0, end=2.0),
            pretty_midi.Note(velocity=100, pitch=53, start=1.0, end=2.0),
        ]
    )

    rhythm = pretty_midi.Instrument(program=2)
    rhythm.notes.extend(
        [
            pretty_midi.Note(velocity=100, pitch=36, start=0.0, end=0.25),
            pretty_midi.Note(velocity=100, pitch=36, start=0.5, end=0.75),
        ]
    )

    midi.instruments.extend([melody, harmony, rhythm])
    return midi


class MelodyExtractorTestCase(unittest.TestCase):
    def test_extract_returns_pitch_and_duration(self) -> None:
        midi = _build_polyphonic_midi()
        extractor = MelodyExtractor()

        result = extractor.extract(midi)

        self.assertEqual(
            result,
            [
                {"pitch": 64, "duration": 0.25},
                {"pitch": 36, "duration": 0.25},
                {"pitch": 67, "duration": 0.5},
            ],
        )


class HarmonyExtractorTestCase(unittest.TestCase):
    def test_extract_groups_simultaneous_notes_as_chords(self) -> None:
        midi = _build_polyphonic_midi()
        extractor = HarmonyExtractor()

        result = extractor.extract(midi)

        self.assertEqual(
            result,
            [
                {"start": 0.0, "end": 1.0, "chord": "C2-C3-E3-G3-C4-E4"},
                {"start": 0.5, "end": 0.75, "chord": "C2"},
                {"start": 1.0, "end": 2.0, "chord": "D3-F3-G4"},
            ],
        )


class RhythmExtractorTestCase(unittest.TestCase):
    def test_extract_returns_onset_and_duration(self) -> None:
        midi = _build_polyphonic_midi()
        extractor = RhythmExtractor()

        result = extractor.extract(midi)

        self.assertEqual(
            result,
            [
                {"onset": 0.0, "duration": 0.25},
                {"onset": 0.0, "duration": 0.25},
                {"onset": 0.0, "duration": 0.5},
                {"onset": 0.0, "duration": 1.0},
                {"onset": 0.0, "duration": 1.0},
                {"onset": 0.0, "duration": 1.0},
                {"onset": 0.5, "duration": 0.25},
                {"onset": 1.0, "duration": 0.5},
                {"onset": 1.0, "duration": 1.0},
                {"onset": 1.0, "duration": 1.0},
            ],
        )


if __name__ == "__main__":
    unittest.main()
