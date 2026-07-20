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

transform_combined = import_module("experiment.10_transform_combined").transform_combined


def _create_combined_representations_dataset(root: Path, count: int) -> Path:
    representations_root = root / "data" / "processed" / "representations"
    representations_root.mkdir(parents=True, exist_ok=True)

    for index in range(1, count + 1):
        payload = {
            "segment_file": f"{index:03d}_segment_01.mid",
            "melody": [
                {"pitch": 60, "duration": 0.5},
                {"pitch": 62, "duration": 0.25},
            ],
            "harmony": [
                {"start": 0.0, "end": 0.5, "chord": "C4-E4-G4"},
                {"start": 0.5, "end": 1.0, "chord": "F4-A4-C5"},
            ],
            "rhythm": [
                {"onset": 0.0, "duration": 0.5},
                {"onset": 0.5, "duration": 0.25},
            ],
        }
        (representations_root / f"{index:03d}_segment_01.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return representations_root


class TransformCombinedTestCase(unittest.TestCase):
    def test_transform_combined_creates_outputs_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_path = _create_combined_representations_dataset(root, 2)
            output_path = root / "data" / "processed" / "transformations"
            section = {
                "random_seed": 42,
                "enabled": ["melody_harmony"],
                "melody_harmony": {
                    "melody": {
                        "transformation": "transpose",
                        "parameters": {"semitones": 2},
                    },
                    "harmony": {
                        "transformation": "chord_substitution",
                        "parameters": {"strength": 0.25},
                    },
                },
            }

            result = transform_combined(source_path, output_path, section)

            self.assertEqual(result, output_path / "combined")
            combo_root = next((result / "melody_harmony").iterdir())
            self.assertEqual(combo_root.parent.parent.name, "combined")
            json_files = sorted(path.name for path in combo_root.glob("*.json"))
            self.assertEqual(json_files, ["001_segment_01.json", "002_segment_01.json"])

            metadata_path = combo_root / "metadata.csv"
            self.assertTrue(metadata_path.exists())
            with metadata_path.open("r", encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["combination"], "melody_harmony")
            self.assertIn("melody", rows[0]["individual_transformations"])
            self.assertIn("harmony", rows[0]["individual_transformations"])

    def test_transform_combined_reuses_existing_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_path = _create_combined_representations_dataset(root, 1)
            output_path = root / "data" / "processed" / "transformations"
            section = {
                "random_seed": 42,
                "enabled": ["melody_harmony"],
                "melody_harmony": {
                    "melody": {
                        "transformation": "transpose",
                        "parameters": {"semitones": 2},
                    },
                    "harmony": {
                        "transformation": "chord_substitution",
                        "parameters": {"strength": 0.25},
                    },
                },
            }

            first_result = transform_combined(source_path, output_path, section)
            first_combo_root = next((first_result / "melody_harmony").iterdir())
            existing_json = next(first_combo_root.glob("*.json"))
            existing_content = existing_json.read_text(encoding="utf-8")

            with patch(
                "experiment.10_transform_combined.MelodyHarmonyTransformation.transform"
            ) as mocked_transform:
                second_result = transform_combined(source_path, output_path, section)

            mocked_transform.assert_not_called()
            self.assertEqual(first_result, second_result)
            self.assertEqual(existing_json.read_text(encoding="utf-8"), existing_content)


if __name__ == "__main__":
    unittest.main()
