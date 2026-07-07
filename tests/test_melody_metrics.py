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

from experiment.compute_melody_metrics import compute_melody_metrics
from metrics.melody.edit_distance import EditDistanceMetric
from metrics.melody.interval_ngram_similarity import IntervalNGramSimilarityMetric
from metrics.melody.longest_common_subsequence import LongestCommonSubsequenceMetric
from preprocessing.representation.melody_representation import MelodyRepresentation


def _build_melody_representation(pitches: list[int]) -> MelodyRepresentation:
    return MelodyRepresentation.from_dict(
        {
            "segment_file": "001_segment_01.mid",
            "melody": [{"pitch": pitch, "duration": 0.5} for pitch in pitches],
        }
    )


def _create_transformations_fixture(root: Path) -> tuple[Path, Path]:
    representations_root = root / "data" / "processed" / "representations"
    transformations_root = root / "data" / "processed" / "transformations"
    representations_root.mkdir(parents=True, exist_ok=True)

    original_payload = {
        "segment_file": "001_segment_01.mid",
        "melody": [
            {"pitch": 60, "duration": 0.5},
            {"pitch": 62, "duration": 0.5},
            {"pitch": 64, "duration": 0.5},
            {"pitch": 65, "duration": 0.5},
        ],
    }
    (representations_root / "001_segment_01.json").write_text(
        json.dumps(original_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    metadata_root = transformations_root / "melody" / "transpose" / "semitones_2"
    metadata_root.mkdir(parents=True, exist_ok=True)
    transformed_payload = {
        "segment_file": "001_segment_01.mid",
        "melody": [
            {"pitch": 62, "duration": 0.5},
            {"pitch": 64, "duration": 0.5},
            {"pitch": 66, "duration": 0.5},
            {"pitch": 67, "duration": 0.5},
        ],
        "transformation": "transpose",
        "parameters": {"semitones": 2},
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
                "transformation": "transpose",
                "parameters": json.dumps({"semitones": 2}, ensure_ascii=False),
                "source_file": "001_segment_01.json",
                "generated_file": "001_segment_01.json",
            }
        )

    return representations_root, transformations_root


class MelodyMetricsTestCase(unittest.TestCase):
    def test_interval_ngram_similarity_for_identical_representations(self) -> None:
        original = _build_melody_representation([60, 62, 64, 65])
        transformed = _build_melody_representation([60, 62, 64, 65])

        value = IntervalNGramSimilarityMetric().compute(original, transformed, n=2)

        self.assertEqual(value, 1.0)

    def test_interval_ngram_similarity_for_completely_different_representations(self) -> None:
        original = _build_melody_representation([60, 61, 62])
        transformed = _build_melody_representation([70, 68, 66])

        value = IntervalNGramSimilarityMetric().compute(original, transformed, n=2)

        self.assertEqual(value, 0.0)

    def test_interval_ngram_similarity_for_simple_transposition(self) -> None:
        original = _build_melody_representation([60, 62, 64, 65])
        transformed = _build_melody_representation([63, 65, 67, 68])

        value = IntervalNGramSimilarityMetric().compute(original, transformed, n=2)

        self.assertEqual(value, 1.0)

    def test_interval_ngram_similarity_for_interval_modification(self) -> None:
        original = _build_melody_representation([60, 62, 64, 65])
        transformed = _build_melody_representation([60, 63, 64, 66])

        value = IntervalNGramSimilarityMetric().compute(original, transformed, n=2)

        self.assertLess(value, 1.0)

    def test_interval_ngram_similarity_for_empty_melodies(self) -> None:
        original = _build_melody_representation([])
        transformed = _build_melody_representation([])

        value = IntervalNGramSimilarityMetric().compute(original, transformed, n=2)

        self.assertEqual(value, 1.0)

    def test_lcs_for_identical_representations(self) -> None:
        original = _build_melody_representation([60, 62, 64, 65])
        transformed = _build_melody_representation([60, 62, 64, 65])

        value = LongestCommonSubsequenceMetric().compute(original, transformed)

        self.assertEqual(value, 1.0)

    def test_lcs_for_simple_transposition(self) -> None:
        original = _build_melody_representation([60, 62, 64, 65])
        transformed = _build_melody_representation([63, 65, 67, 68])

        value = LongestCommonSubsequenceMetric().compute(original, transformed)

        self.assertEqual(value, 1.0)

    def test_lcs_for_completely_different_representations(self) -> None:
        original = _build_melody_representation([60, 61, 62])
        transformed = _build_melody_representation([70, 68, 66])

        value = LongestCommonSubsequenceMetric().compute(original, transformed)

        self.assertEqual(value, 0.0)

    def test_lcs_for_empty_melodies(self) -> None:
        original = _build_melody_representation([])
        transformed = _build_melody_representation([])

        value = LongestCommonSubsequenceMetric().compute(original, transformed)

        self.assertEqual(value, 1.0)

    def test_edit_distance_for_identical_representations(self) -> None:
        original = _build_melody_representation([60, 62, 64, 65])
        transformed = _build_melody_representation([60, 62, 64, 65])

        value = EditDistanceMetric().compute(original, transformed)

        self.assertEqual(value, 1.0)

    def test_edit_distance_for_simple_transposition(self) -> None:
        original = _build_melody_representation([60, 62, 64, 65])
        transformed = _build_melody_representation([63, 65, 67, 68])

        value = EditDistanceMetric().compute(original, transformed)

        self.assertEqual(value, 1.0)

    def test_edit_distance_for_completely_different_representations(self) -> None:
        original = _build_melody_representation([60, 61, 62])
        transformed = _build_melody_representation([70, 68, 66])

        value = EditDistanceMetric().compute(original, transformed)

        self.assertEqual(value, 0.0)

    def test_edit_distance_for_different_sequence_lengths(self) -> None:
        original = _build_melody_representation([60, 62, 64])
        transformed = _build_melody_representation([60, 62, 64, 65, 67])

        value = EditDistanceMetric().compute(original, transformed)

        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_metrics_handle_one_empty_melody(self) -> None:
        original = _build_melody_representation([])
        transformed = _build_melody_representation([60, 62, 64])

        interval_value = IntervalNGramSimilarityMetric().compute(original, transformed, n=2)
        lcs_value = LongestCommonSubsequenceMetric().compute(original, transformed)
        edit_value = EditDistanceMetric().compute(original, transformed)

        self.assertEqual(interval_value, 0.0)
        self.assertEqual(lcs_value, 0.0)
        self.assertEqual(edit_value, 0.0)


class ComputeMelodyMetricsPipelineTestCase(unittest.TestCase):
    def test_compute_melody_metrics_creates_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            representations_root, transformations_root = _create_transformations_fixture(root)
            output_root = root / "data" / "results" / "compute_metrics"

            result = compute_melody_metrics(
                transformations_path=transformations_root,
                representations_path=representations_root,
                output_path=output_root,
                interval_ngram_n=2,
            )

            self.assertEqual(result, output_root / "melody")
            csv_path = output_root / "melody" / "melody_similarity_metrics.csv"
            self.assertTrue(csv_path.exists())
            with csv_path.open("r", encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(len(rows), 6)
            self.assertEqual({row["metric"] for row in rows}, {
                "interval_ngram_similarity",
                "longest_common_subsequence",
                "edit_distance",
            })
            self.assertEqual({row["comparison_type"] for row in rows}, {
                "transformed",
                "baseline_original",
            })
            baseline_rows = [row for row in rows if row["comparison_type"] == "baseline_original"]
            self.assertTrue(all(row["value"] == "1.000000" for row in baseline_rows))

    def test_compute_melody_metrics_reuses_existing_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            representations_root, transformations_root = _create_transformations_fixture(root)
            output_root = root / "data" / "results" / "compute_metrics"

            compute_melody_metrics(
                transformations_path=transformations_root,
                representations_path=representations_root,
                output_path=output_root,
                interval_ngram_n=2,
            )

            with patch(
                "experiment.compute_melody_metrics.IntervalNGramSimilarityMetric.compute"
            ) as mocked_interval, patch(
                "experiment.compute_melody_metrics.LongestCommonSubsequenceMetric.compute"
            ) as mocked_lcs, patch(
                "experiment.compute_melody_metrics.EditDistanceMetric.compute"
            ) as mocked_edit:
                compute_melody_metrics(
                    transformations_path=transformations_root,
                    representations_path=representations_root,
                    output_path=output_root,
                    interval_ngram_n=2,
                )

            mocked_interval.assert_not_called()
            mocked_lcs.assert_not_called()
            mocked_edit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
