from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pretty_midi

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from experiment.extract_representations import extract_representations


def _write_midi(path: Path) -> None:
    midi = pretty_midi.PrettyMIDI(initial_tempo=120)
    instrument = pretty_midi.Instrument(program=0)
    for index in range(8):
        start = index * 0.5
        instrument.notes.append(
            pretty_midi.Note(
                velocity=100,
                pitch=60 + index,
                start=start,
                end=start + 0.5,
            )
        )
    midi.instruments.append(instrument)
    midi.write(str(path))


def _create_segments_dataset(root: Path, count: int) -> Path:
    segments_root = root / "segments"
    segments_root.mkdir(parents=True, exist_ok=True)

    for index in range(1, count + 1):
        _write_midi(segments_root / f"{index:03d}_segment_01.mid")

    (segments_root / "segments_metadata.csv").write_text(
        "source_file,segment_file,start_measure,end_measure,measures,start_time_seconds,end_time_seconds,random_seed\n",
        encoding="utf-8",
    )
    return segments_root


def _build_loaded_segment() -> pretty_midi.PrettyMIDI:
    midi = pretty_midi.PrettyMIDI(initial_tempo=120)
    instrument = pretty_midi.Instrument(program=0)
    for index in range(8):
        start = index * 0.5
        instrument.notes.append(
            pretty_midi.Note(
                velocity=100,
                pitch=60 + index,
                start=start,
                end=start + 0.5,
            )
        )
    midi.instruments.append(instrument)
    midi.get_downbeats = lambda: np.array([float(index) for index in range(8)], dtype=float)
    return midi


class ExtractRepresentationsTestCase(unittest.TestCase):
    def test_extract_representations_raises_for_missing_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "missing"
            output_path = Path(tmpdir) / "data" / "processed" / "representations"

            with self.assertRaises(FileNotFoundError):
                extract_representations(source_path, output_path)

    def test_extract_representations_creates_json_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_path = _create_segments_dataset(root, 2)
            output_path = root / "data" / "processed" / "representations"

            with patch(
                "experiment.extract_representations.POP909Loader.load_midi_file",
                return_value=_build_loaded_segment(),
            ):
                result = extract_representations(source_path, output_path)

            self.assertEqual(result, output_path)
            json_files = sorted(path.name for path in output_path.iterdir())
            self.assertEqual(
                json_files,
                ["001_segment_01.json", "002_segment_01.json"],
            )

            payload = json.loads((output_path / "001_segment_01.json").read_text(encoding="utf-8"))
            self.assertIn("melody", payload)
            self.assertIn("harmony", payload)
            self.assertIn("rhythm", payload)

    def test_extract_representations_skips_existing_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_path = _create_segments_dataset(root, 1)
            output_path = root / "data" / "processed" / "representations"
            output_path.mkdir(parents=True, exist_ok=True)
            existing_json = output_path / "001_segment_01.json"
            existing_json.write_text("{\"existing\": true}", encoding="utf-8")

            with patch(
                "experiment.extract_representations.POP909Loader.load_midi_file"
            ) as mocked_load:
                extract_representations(source_path, output_path)

            mocked_load.assert_not_called()
            self.assertEqual(
                existing_json.read_text(encoding="utf-8"),
                "{\"existing\": true}",
            )


if __name__ == "__main__":
    unittest.main()
