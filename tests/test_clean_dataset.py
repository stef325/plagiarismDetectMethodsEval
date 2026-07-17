from __future__ import annotations

import tempfile
import unittest
import sys
from importlib import import_module
from pathlib import Path

import pretty_midi

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

clean_dataset = import_module("experiment.02_clean_dataset").clean_dataset


def _write_midi(path: Path) -> None:
    midi = pretty_midi.PrettyMIDI(initial_tempo=120)
    instrument = pretty_midi.Instrument(program=0)
    instrument.notes.append(
        pretty_midi.Note(velocity=100, pitch=60, start=0.0, end=0.5)
    )
    midi.instruments.append(instrument)
    midi.write(str(path))


def _create_music_dir(root: Path, song_id: str) -> Path:
    music_dir = root / song_id
    music_dir.mkdir(parents=True, exist_ok=True)

    _write_midi(music_dir / f"{song_id}.mid")
    versions_dir = music_dir / "versions"
    versions_dir.mkdir(exist_ok=True)
    _write_midi(versions_dir / f"{song_id}-v1.mid")
    (music_dir / "notes.txt").write_text("texto auxiliar", encoding="utf-8")

    return music_dir


class CleanDatasetTestCase(unittest.TestCase):
    def test_clean_dataset_raises_for_missing_dataset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset_path = Path(tmpdir) / "missing"
            processed_path = Path(tmpdir) / "data" / "processed"

            with self.assertRaises(FileNotFoundError):
                clean_dataset(dataset_path, processed_path)

    def test_clean_dataset_copies_only_main_midis(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset_root = Path(tmpdir) / "POP909"
            processed_path = Path(tmpdir) / "data" / "processed"
            _create_music_dir(dataset_root, "001")
            _create_music_dir(dataset_root, "002")

            result = clean_dataset(dataset_root, processed_path)

            expected_root = processed_path / "POP909"
            self.assertEqual(result, expected_root)
            self.assertTrue((expected_root / "001.mid").exists())
            self.assertTrue((expected_root / "002.mid").exists())
            self.assertEqual(
                sorted(path.name for path in expected_root.iterdir()),
                ["001.mid", "002.mid"],
            )

    def test_clean_dataset_replaces_previous_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset_root = Path(tmpdir) / "POP909"
            processed_path = Path(tmpdir) / "data" / "processed"
            _create_music_dir(dataset_root, "001")

            stale_target = processed_path / "POP909" / "stale.mid"
            stale_target.parent.mkdir(parents=True, exist_ok=True)
            stale_target.write_text("arquivo antigo", encoding="utf-8")

            clean_dataset(dataset_root, processed_path)

            expected_root = processed_path / "POP909"
            self.assertTrue((expected_root / "001.mid").exists())
            self.assertFalse((expected_root / "stale.mid").exists())


if __name__ == "__main__":
    unittest.main()
