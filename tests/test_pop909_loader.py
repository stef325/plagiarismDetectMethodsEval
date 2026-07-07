from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pretty_midi

from src.preprocessing.dataset.pop909_loader import POP909Loader


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
    _write_midi(versions_dir / f"{song_id}-v2.mid")

    return music_dir


def _create_empty_music_dir(root: Path, song_id: str) -> Path:
    music_dir = root / song_id
    music_dir.mkdir(parents=True, exist_ok=True)
    return music_dir


def _create_music_dir_with_unexpected_files(root: Path, song_id: str) -> Path:
    music_dir = _create_music_dir(root, song_id)
    (music_dir / "notes.txt").write_text("texto inesperado", encoding="utf-8")
    (music_dir / "cover.png").write_bytes(b"not a midi")
    (music_dir / "versions" / "readme.txt").write_text("texto", encoding="utf-8")
    return music_dir


class POP909LoaderTestCase(unittest.TestCase):
    def test_get_music_directory_returns_existing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            expected_dir = _create_music_dir(root, "001")
            loader = POP909Loader(root)

            self.assertEqual(loader.get_music_directory("001"), expected_dir)

    def test_get_music_directory_raises_for_missing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = POP909Loader(Path(tmpdir))

            with self.assertRaises(FileNotFoundError):
                loader.get_music_directory("999")

    def test_list_music_midi_files_returns_sorted_mid_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _create_music_dir(root, "001")
            loader = POP909Loader(root)

            result = loader.list_music_midi_files("001")

            self.assertEqual(
                [path.relative_to(root).as_posix() for path in result],
                ["001/001.mid", "001/versions/001-v1.mid", "001/versions/001-v2.mid"],
            )

    def test_list_music_midi_files_returns_empty_list_for_empty_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _create_empty_music_dir(root, "001")
            loader = POP909Loader(root)

            result = loader.list_music_midi_files("001")

            self.assertEqual(result, [])

    def test_list_music_midi_files_ignores_unexpected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _create_music_dir_with_unexpected_files(root, "001")
            loader = POP909Loader(root)

            result = loader.list_music_midi_files("001")

            self.assertEqual(
                [path.relative_to(root).as_posix() for path in result],
                ["001/001.mid", "001/versions/001-v1.mid", "001/versions/001-v2.mid"],
            )
            self.assertTrue(all(path.suffix == ".mid" for path in result))

    def test_load_music_returns_pretty_midi_objects(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _create_music_dir(root, "001")
            loader = POP909Loader(root)

            result = loader.load_music("001")

            self.assertEqual(
                sorted(path.as_posix() for path in result.keys()),
                ["001/001.mid", "001/versions/001-v1.mid", "001/versions/001-v2.mid"],
            )
            self.assertTrue(
                all(isinstance(value, pretty_midi.PrettyMIDI) for value in result.values())
            )

    def test_load_music_returns_only_midi_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _create_music_dir_with_unexpected_files(root, "001")
            loader = POP909Loader(root)

            result = loader.load_music("001")

            self.assertEqual(
                sorted(path.as_posix() for path in result.keys()),
                ["001/001.mid", "001/versions/001-v1.mid", "001/versions/001-v2.mid"],
            )
            self.assertTrue(all(path.suffix == ".mid" for path in result.keys()))

    def test_load_music_raises_for_missing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = POP909Loader(Path(tmpdir))

            with self.assertRaises(FileNotFoundError):
                loader.load_music("999")

    def test_load_music_raises_for_corrupted_midi(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            music_dir = _create_empty_music_dir(root, "001")
            corrupted_midi = music_dir / "001.mid"
            corrupted_midi.write_text("not a midi file", encoding="utf-8")
            loader = POP909Loader(root)

            with self.assertRaises(OSError):
                loader.load_music("001")


if __name__ == "__main__":
    unittest.main()
