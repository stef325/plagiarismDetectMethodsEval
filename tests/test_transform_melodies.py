from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from importlib import import_module
from pathlib import Path
from unittest.mock import patch

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

transform_melodies = import_module("experiment.07_transform_melodies").transform_melodies


def _create_representations_dataset(root: Path, count: int) -> Path:
    representations_root = root / "data" / "processed" / "representations"
    representations_root.mkdir(parents=True, exist_ok=True)

    for index in range(1, count + 1):
        payload = {
            "segment_file": f"{index:03d}_segment_01.mid",
            "melody": [
                {"pitch": 60, "duration": 0.5},
                {"pitch": 62, "duration": 0.25},
                {"pitch": 64, "duration": 0.5},
            ],
            "harmony": [{"start": 0.0, "end": 1.0, "chord": "C4"}],
            "rhythm": [{"onset": 0.0, "duration": 0.5}],
        }
        (representations_root / f"{index:03d}_segment_01.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return representations_root


class TransformMelodiesTestCase(unittest.TestCase):
    def test_transform_melodies_creates_parameterized_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_path = _create_representations_dataset(root, 2)
            output_path = root / "data" / "processed" / "transformations"

            result = transform_melodies(
                source_path,
                output_path,
                transformation_name="transpose",
                parameters={"semitones": 2},
                random_seed=42,
            )

            self.assertEqual(result.parts[-3:-1], ("melody", "transpose"))
            json_files = sorted(path.name for path in result.glob("*.json"))
            self.assertEqual(json_files, ["001_segment_01.json", "002_segment_01.json"])

            metadata_path = result / "metadata.csv"
            self.assertTrue(metadata_path.exists())
            with metadata_path.open("r", encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["song_id"], "001")
            self.assertEqual(rows[0]["segment_id"], "01")
            self.assertEqual(rows[0]["transformation"], "transpose")
            self.assertIn("semitones", rows[0]["parameters"])

    def test_transform_melodies_reuses_existing_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_path = _create_representations_dataset(root, 1)
            output_path = root / "data" / "processed" / "transformations"

            first_result = transform_melodies(
                source_path,
                output_path,
                transformation_name="transpose",
                parameters={"semitones": 2},
                random_seed=42,
            )
            existing_json = next(first_result.glob("*.json"))
            existing_content = existing_json.read_text(encoding="utf-8")

            with patch(
                "experiment.07_transform_melodies.TranspositionTransformation.transform"
            ) as mocked_transform:
                second_result = transform_melodies(
                    source_path,
                    output_path,
                    transformation_name="transpose",
                    parameters={"semitones": 2},
                    random_seed=42,
                )

            mocked_transform.assert_not_called()
            self.assertEqual(first_result, second_result)
            self.assertEqual(existing_json.read_text(encoding="utf-8"), existing_content)


if __name__ == "__main__":
    unittest.main()
