from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import pretty_midi

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from experiment.select_subset import select_subset


def _write_midi(path: Path) -> None:
    midi = pretty_midi.PrettyMIDI(initial_tempo=120)
    instrument = pretty_midi.Instrument(program=0)
    instrument.notes.append(
        pretty_midi.Note(velocity=100, pitch=60, start=0.0, end=0.5)
    )
    midi.instruments.append(instrument)
    midi.write(str(path))


def _create_processed_dataset(root: Path, count: int) -> Path:
    dataset_root = root / "POP909"
    dataset_root.mkdir(parents=True, exist_ok=True)

    for index in range(1, count + 1):
        midi_path = dataset_root / f"{index:03d}.mid"
        _write_midi(midi_path)

    (dataset_root / "notes.txt").write_text("arquivo auxiliar", encoding="utf-8")
    return dataset_root


class SelectSubsetTestCase(unittest.TestCase):
    def test_select_subset_raises_for_missing_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "missing"
            output_path = Path(tmpdir) / "data" / "processed" / "subset"

            with self.assertRaises(FileNotFoundError):
                select_subset(source_path, output_path, sample_size=1, random_seed=42)

    def test_select_subset_creates_reproducible_subset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_path = _create_processed_dataset(root, 5)
            output_path = root / "data" / "processed" / "subset"

            first_result = select_subset(
                source_path,
                output_path,
                sample_size=3,
                random_seed=42,
            )
            first_files = sorted(path.name for path in first_result.iterdir())

            second_result = select_subset(
                source_path,
                output_path,
                sample_size=3,
                random_seed=42,
            )
            second_files = sorted(path.name for path in second_result.iterdir())

            self.assertEqual(first_result, output_path)
            self.assertEqual(second_result, output_path)
            self.assertEqual(first_files, second_files)
            self.assertEqual(len(first_files), 3)
            self.assertTrue(all(name.endswith(".mid") for name in first_files))
            self.assertNotIn("notes.txt", first_files)

    def test_select_subset_raises_when_sample_size_exceeds_available_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_path = _create_processed_dataset(root, 2)
            output_path = root / "data" / "processed" / "subset"

            with self.assertRaises(ValueError):
                select_subset(source_path, output_path, sample_size=3, random_seed=42)


if __name__ == "__main__":
    unittest.main()
