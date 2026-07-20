from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from importlib import import_module
from pathlib import Path

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

validate_representations = import_module(
    "experiment.11_validate_representations"
).validate_representations


def _create_segments_metadata(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "source_file",
                "segment_file",
                "start_measure",
                "end_measure",
                "measures",
                "start_time_seconds",
                "end_time_seconds",
                "random_seed",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def _write_representation_json(
    path: Path,
    segment_file: str,
    melody: list[dict[str, int | float]],
    harmony: list[dict[str, int | float | str]],
    rhythm: list[dict[str, int | float]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "segment_file": segment_file,
        "melody": melody,
        "harmony": harmony,
        "rhythm": rhythm,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class ValidateRepresentationsTestCase(unittest.TestCase):
    def test_validate_representations_raises_for_missing_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            representations_path = Path(tmpdir) / "missing"
            metadata_path = Path(tmpdir) / "segments_metadata.csv"
            report_path = Path(tmpdir) / "data" / "results" / "report.md"

            with self.assertRaises(FileNotFoundError):
                validate_representations(representations_path, metadata_path, report_path)

    def test_validate_representations_writes_success_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            representations_path = root / "data" / "processed" / "representations"
            metadata_path = root / "data" / "processed" / "segments" / "segments_metadata.csv"
            report_path = root / "data" / "results" / "validate_representations" / "report.md"

            _create_segments_metadata(
                metadata_path,
                [
                    {
                        "source_file": "001.mid",
                        "segment_file": "001_segment_01.mid",
                        "start_measure": "1",
                        "end_measure": "8",
                        "measures": "8",
                        "start_time_seconds": "0.000000",
                        "end_time_seconds": "16.000000",
                        "random_seed": "42",
                    },
                    {
                        "source_file": "002.mid",
                        "segment_file": "002_segment_01.mid",
                        "start_measure": "9",
                        "end_measure": "16",
                        "measures": "8",
                        "start_time_seconds": "16.000000",
                        "end_time_seconds": "32.000000",
                        "random_seed": "42",
                    },
                ],
            )

            _write_representation_json(
                representations_path / "001_segment_01.json",
                "001_segment_01.mid",
                melody=[{"pitch": 60, "duration": 0.5}],
                harmony=[{"start": 0.0, "end": 1.0, "chord": "C4"}],
                rhythm=[{"onset": 0.0, "duration": 0.5}],
            )
            _write_representation_json(
                representations_path / "002_segment_01.json",
                "002_segment_01.mid",
                melody=[{"pitch": 62, "duration": 0.5}],
                harmony=[{"start": 0.0, "end": 1.0, "chord": "D4"}],
                rhythm=[{"onset": 0.0, "duration": 0.5}],
            )

            validate_representations(representations_path, metadata_path, report_path)

            content = report_path.read_text(encoding="utf-8")
            self.assertIn("- Representacoes extraidas: 2", content)
            self.assertIn("- Melodias validas: 2", content)
            self.assertIn("- Harmonias validas: 2", content)
            self.assertIn("- Ritmos validos: 2", content)
            self.assertIn("- Falhas: 0", content)
            self.assertIn("Nenhuma falha encontrada.", content)

    def test_validate_representations_reports_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            representations_path = root / "data" / "processed" / "representations"
            metadata_path = root / "data" / "processed" / "segments" / "segments_metadata.csv"
            report_path = root / "data" / "results" / "validate_representations" / "report.md"

            _create_segments_metadata(
                metadata_path,
                [
                    {
                        "source_file": "001.mid",
                        "segment_file": "001_segment_01.mid",
                        "start_measure": "1",
                        "end_measure": "8",
                        "measures": "8",
                        "start_time_seconds": "0.000000",
                        "end_time_seconds": "16.000000",
                        "random_seed": "42",
                    }
                ],
            )

            _write_representation_json(
                representations_path / "001_segment_01.json",
                "001_segment_01.mid",
                melody=[],
                harmony=[{"start": 0.0, "end": 1.0, "chord": "C4"}],
                rhythm=[],
            )

            validate_representations(representations_path, metadata_path, report_path)

            content = report_path.read_text(encoding="utf-8")
            self.assertIn("- Representacoes extraidas: 1", content)
            self.assertIn("- Melodias validas: 0", content)
            self.assertIn("- Harmonias validas: 1", content)
            self.assertIn("- Ritmos validos: 0", content)
            self.assertIn("- Falhas: 2", content)
            self.assertIn("MelodiaVazia", content)
            self.assertIn("RitmoVazio", content)


if __name__ == "__main__":
    unittest.main()
