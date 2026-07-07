from __future__ import annotations

import sys
import tempfile
import unittest
import csv
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pretty_midi

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from experiment.extract_segments import extract_segments


def _write_midi(path: Path) -> None:
    midi = pretty_midi.PrettyMIDI(initial_tempo=120)
    instrument = pretty_midi.Instrument(program=0)
    instrument.notes.append(
        pretty_midi.Note(velocity=100, pitch=60, start=0.0, end=0.5)
    )
    midi.instruments.append(instrument)
    midi.write(str(path))


def _create_subset_dataset(root: Path, count: int) -> Path:
    subset_root = root / "subset"
    subset_root.mkdir(parents=True, exist_ok=True)

    for index in range(1, count + 1):
        _write_midi(subset_root / f"{index:03d}.mid")

    return subset_root


def _build_loaded_midi() -> pretty_midi.PrettyMIDI:
    midi = pretty_midi.PrettyMIDI(initial_tempo=120)
    instrument = pretty_midi.Instrument(program=0)
    for index in range(24):
        start = index * 0.5
        instrument.notes.append(
            pretty_midi.Note(
                velocity=100,
                pitch=60 + (index % 12),
                start=start,
                end=start + 0.25,
            )
        )
    midi.instruments.append(instrument)
    midi.get_downbeats = lambda: np.array(
        [float(index) for index in range(10)],
        dtype=float,
    )
    return midi


class ExtractSegmentsTestCase(unittest.TestCase):
    def test_extract_segments_raises_for_missing_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "missing"
            output_path = Path(tmpdir) / "data" / "processed" / "segments"

            with self.assertRaises(FileNotFoundError):
                extract_segments(
                    source_path,
                    output_path,
                    measures_per_segment=2,
                    segments_per_song=1,
                    random_seed=42,
                )

    def test_extract_segments_creates_flat_segment_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_path = _create_subset_dataset(root, 2)
            output_path = root / "data" / "processed" / "segments"

            with patch(
                "experiment.extract_segments.POP909Loader.load_midi_file",
                return_value=_build_loaded_midi(),
            ):
                result = extract_segments(
                    source_path,
                    output_path,
                    measures_per_segment=2,
                    segments_per_song=2,
                    random_seed=42,
                )

            self.assertEqual(result, output_path)
            self.assertEqual(
                sorted(path.name for path in output_path.iterdir()),
                [
                    "001_segment_01.mid",
                    "001_segment_02.mid",
                    "002_segment_01.mid",
                    "002_segment_02.mid",
                    "segments_metadata.csv",
                ],
            )

            metadata_path = output_path / "segments_metadata.csv"
            self.assertTrue(metadata_path.exists())

            with metadata_path.open("r", encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(len(rows), 4)
            self.assertTrue(all(row["measures"] == "2" for row in rows))
            self.assertTrue(all(row["segment_file"].endswith(".mid") for row in rows))
            self.assertEqual(
                {row["source_file"] for row in rows},
                {"001.mid", "002.mid"},
            )

    def test_extract_segments_is_reproducible_with_same_seed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_path = _create_subset_dataset(root, 1)
            first_output = root / "data" / "processed" / "segments_first"
            second_output = root / "data" / "processed" / "segments_second"

            with patch(
                "experiment.extract_segments.POP909Loader.load_midi_file",
                return_value=_build_loaded_midi(),
            ):
                extract_segments(
                    source_path,
                    first_output,
                    measures_per_segment=2,
                    segments_per_song=2,
                    random_seed=99,
                )

            with patch(
                "experiment.extract_segments.POP909Loader.load_midi_file",
                return_value=_build_loaded_midi(),
            ):
                extract_segments(
                    source_path,
                    second_output,
                    measures_per_segment=2,
                    segments_per_song=2,
                    random_seed=99,
                )

            first_files = sorted(path.name for path in first_output.iterdir())
            second_files = sorted(path.name for path in second_output.iterdir())
            self.assertEqual(first_files, second_files)
            self.assertEqual(
                first_files,
                ["001_segment_01.mid", "001_segment_02.mid", "segments_metadata.csv"],
            )


if __name__ == "__main__":
    unittest.main()
