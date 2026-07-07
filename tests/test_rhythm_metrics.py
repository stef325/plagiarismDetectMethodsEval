from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from experiment.compute_rhythm_metrics import compute_rhythm_metrics
from metrics.rhythm.ioi_similarity import IoISimilarityMetric
from metrics.rhythm.rhythm_ngram_similarity import RhythmNGramSimilarityMetric
from metrics.rhythm.rhythmic_edit_distance import RhythmicEditDistanceMetric
from preprocessing.representation.rhythm_representation import RhythmRepresentation


def _build_rhythm_representation(events: list[tuple[float, float]]) -> RhythmRepresentation:
    return RhythmRepresentation.from_dict(
        {
            "segment_file": "001_segment_01.mid",
            "rhythm": [
                {"onset": onset, "duration": duration}
                for onset, duration in events
            ],
        }
    )


def _create_transformations_fixture(root: Path) -> tuple[Path, Path]:
    representations_root = root / "data" / "processed" / "representations"
    transformations_root = root / "data" / "processed" / "transformations"
    representations_root.mkdir(parents=True, exist_ok=True)

    original_payload = {
        "segment_file": "001_segment_01.mid",
        "rhythm": [
            {"onset": 0.0, "duration": 0.5},
            {"onset": 0.5, "duration": 0.5},
            {"onset": 1.0, "duration": 0.5},
            {"onset": 1.5, "duration": 0.5},
        ],
    }
    (representations_root / "001_segment_01.json").write_text(
        json.dumps(original_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    metadata_root = transformations_root / "rhythm" / "tempo_change" / "tempo_factor_0p8"
    metadata_root.mkdir(parents=True, exist_ok=True)
    transformed_payload = {
        "segment_file": "001_segment_01.mid",
        "rhythm": [
            {"onset": 0.0, "duration": 0.4},
            {"onset": 0.4, "duration": 0.4},
            {"onset": 0.8, "duration": 0.4},
            {"onset": 1.2, "duration": 0.4},
        ],
        "transformation": "tempo_change",
        "parameters": {"tempo_factor": 0.8},
    }
    (metadata_root / "001_segment_01.json").write_text(
        json.dumps(transformed_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    with (metadata_root / "metadata.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "song_id",
                "segment_id",
                "transformation",
                "parameters",
                "source_file",
                "generated_file",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "tempo_change",
                "parameters": json.dumps({"tempo_factor": 0.8}, ensure_ascii=False),
                "source_file": "001_segment_01.json",
                "generated_file": "001_segment_01.json",
            }
        )

    return representations_root, transformations_root


class RhythmMetricsTestCase(unittest.TestCase):
    def test_rhythm_ngram_similarity_for_identical_representations(self) -> None:
        original = _build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])
        transformed = _build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])

        value = RhythmNGramSimilarityMetric().compute(original, transformed, n=2)

        self.assertEqual(value, 1.0)

    def test_rhythm_ngram_similarity_for_completely_different_representations(self) -> None:
        original = _build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])
        transformed = _build_rhythm_representation([(0.0, 0.25), (0.35, 0.55), (0.95, 0.15)])

        value = RhythmNGramSimilarityMetric().compute(original, transformed, n=2)

        self.assertLess(value, 1.0)

    def test_rhythm_ngram_similarity_for_tempo_change(self) -> None:
        original = _build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])
        transformed = _build_rhythm_representation([(0.0, 0.4), (0.4, 0.4), (0.8, 0.4)])

        value = RhythmNGramSimilarityMetric().compute(original, transformed, n=2)

        self.assertGreater(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_rhythm_ngram_similarity_for_empty_sequences(self) -> None:
        original = _build_rhythm_representation([])
        transformed = _build_rhythm_representation([])

        value = RhythmNGramSimilarityMetric().compute(original, transformed, n=2)

        self.assertEqual(value, 1.0)

    def test_ioi_similarity_for_identical_representations(self) -> None:
        original = _build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])
        transformed = _build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])

        value = IoISimilarityMetric().compute(original, transformed)

        self.assertEqual(value, 1.0)

    def test_ioi_similarity_for_different_length_sequences(self) -> None:
        original = _build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])
        transformed = _build_rhythm_representation([(0.0, 0.4), (0.4, 0.4)])

        value = IoISimilarityMetric().compute(original, transformed)

        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_ioi_similarity_for_empty_sequences(self) -> None:
        original = _build_rhythm_representation([])
        transformed = _build_rhythm_representation([])

        value = IoISimilarityMetric().compute(original, transformed)

        self.assertEqual(value, 1.0)

    def test_rhythmic_edit_distance_for_identical_representations(self) -> None:
        original = _build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])
        transformed = _build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])

        value = RhythmicEditDistanceMetric().compute(original, transformed)

        self.assertEqual(value, 1.0)

    def test_rhythmic_edit_distance_for_duration_scaling(self) -> None:
        original = _build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])
        transformed = _build_rhythm_representation([(0.0, 0.75), (0.75, 0.75), (1.5, 0.75)])

        value = RhythmicEditDistanceMetric().compute(original, transformed)

        self.assertGreater(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_rhythmic_edit_distance_for_completely_different_representations(self) -> None:
        original = _build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])
        transformed = _build_rhythm_representation([(0.0, 0.25), (0.35, 0.55), (0.95, 0.15)])

        value = RhythmicEditDistanceMetric().compute(original, transformed)

        self.assertLess(value, 1.0)

    def test_rhythmic_edit_distance_for_empty_sequences(self) -> None:
        original = _build_rhythm_representation([])
        transformed = _build_rhythm_representation([])

        value = RhythmicEditDistanceMetric().compute(original, transformed)

        self.assertEqual(value, 1.0)


class ComputeRhythmMetricsPipelineTestCase(unittest.TestCase):
    def test_compute_rhythm_metrics_creates_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            representations_root, transformations_root = _create_transformations_fixture(root)
            output_root = root / "data" / "results" / "compute_metrics"

            result = compute_rhythm_metrics(
                transformations_path=transformations_root,
                representations_path=representations_root,
                output_path=output_root,
                rhythm_ngram_n=2,
            )

            self.assertEqual(result, output_root / "rhythm")
            csv_path = output_root / "rhythm" / "rhythm_similarity_metrics.csv"
            self.assertTrue(csv_path.exists())
            with csv_path.open("r", encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(len(rows), 6)
            self.assertEqual({row["metric"] for row in rows}, {
                "rhythm_ngram_similarity",
                "ioi_similarity",
                "rhythmic_edit_distance",
            })
            self.assertEqual({row["comparison_type"] for row in rows}, {
                "transformed",
                "baseline_original",
            })
            baseline_rows = [row for row in rows if row["comparison_type"] == "baseline_original"]
            self.assertTrue(all(row["value"] == "1.000000" for row in baseline_rows))

    def test_compute_rhythm_metrics_reuses_existing_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            representations_root, transformations_root = _create_transformations_fixture(root)
            output_root = root / "data" / "results" / "compute_metrics"

            compute_rhythm_metrics(
                transformations_path=transformations_root,
                representations_path=representations_root,
                output_path=output_root,
                rhythm_ngram_n=2,
            )

            with patch(
                "experiment.compute_rhythm_metrics.RhythmNGramSimilarityMetric.compute"
            ) as mocked_ngram, patch(
                "experiment.compute_rhythm_metrics.IoISimilarityMetric.compute"
            ) as mocked_ioi, patch(
                "experiment.compute_rhythm_metrics.RhythmicEditDistanceMetric.compute"
            ) as mocked_edit:
                compute_rhythm_metrics(
                    transformations_path=transformations_root,
                    representations_path=representations_root,
                    output_path=output_root,
                    rhythm_ngram_n=2,
                )

            mocked_ngram.assert_not_called()
            mocked_ioi.assert_not_called()
            mocked_edit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
