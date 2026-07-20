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

compute_global_metrics = import_module(
    "experiment.16_compute_global_metrics"
).compute_global_metrics
SimpleAverageMetric = import_module("metrics.global.simple_average").SimpleAverageMetric
WeightedAverageMetric = import_module("metrics.global.weighted_average").WeightedAverageMetric


def _create_metrics_fixture(root: Path) -> Path:
    metrics_root = root / "data" / "results" / "compute_metrics"
    for modality, rows in {
        "melody": [
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "transpose",
                "comparison_type": "transformed",
                "metric": "interval_ngram_similarity",
                "metric_parameters": json.dumps({"n": 2}, ensure_ascii=False),
                "value": "1.000000",
            },
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "transpose",
                "comparison_type": "transformed",
                "metric": "longest_common_subsequence",
                "metric_parameters": "{}",
                "value": "1.000000",
            },
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "transpose",
                "comparison_type": "transformed",
                "metric": "edit_distance",
                "metric_parameters": "{}",
                "value": "1.000000",
            },
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "original_copy",
                "comparison_type": "baseline_original",
                "metric": "interval_ngram_similarity",
                "metric_parameters": json.dumps({"n": 2}, ensure_ascii=False),
                "value": "1.000000",
            },
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "original_copy",
                "comparison_type": "baseline_original",
                "metric": "longest_common_subsequence",
                "metric_parameters": "{}",
                "value": "1.000000",
            },
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "original_copy",
                "comparison_type": "baseline_original",
                "metric": "edit_distance",
                "metric_parameters": "{}",
                "value": "1.000000",
            },
        ],
        "harmony": [
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "transpose",
                "comparison_type": "transformed",
                "metric": "chord_ngram_similarity",
                "metric_parameters": json.dumps({"n": 2}, ensure_ascii=False),
                "value": "0.800000",
            },
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "transpose",
                "comparison_type": "transformed",
                "metric": "harmonic_edit_distance",
                "metric_parameters": "{}",
                "value": "0.700000",
            },
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "transpose",
                "comparison_type": "transformed",
                "metric": "pitch_class_similarity",
                "metric_parameters": "{}",
                "value": "0.600000",
            },
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "original_copy",
                "comparison_type": "baseline_original",
                "metric": "chord_ngram_similarity",
                "metric_parameters": json.dumps({"n": 2}, ensure_ascii=False),
                "value": "1.000000",
            },
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "original_copy",
                "comparison_type": "baseline_original",
                "metric": "harmonic_edit_distance",
                "metric_parameters": "{}",
                "value": "1.000000",
            },
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "original_copy",
                "comparison_type": "baseline_original",
                "metric": "pitch_class_similarity",
                "metric_parameters": "{}",
                "value": "1.000000",
            },
        ],
        "rhythm": [
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "transpose",
                "comparison_type": "transformed",
                "metric": "rhythm_ngram_similarity",
                "metric_parameters": json.dumps({"n": 2}, ensure_ascii=False),
                "value": "0.900000",
            },
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "transpose",
                "comparison_type": "transformed",
                "metric": "ioi_similarity",
                "metric_parameters": "{}",
                "value": "0.850000",
            },
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "transpose",
                "comparison_type": "transformed",
                "metric": "rhythmic_edit_distance",
                "metric_parameters": "{}",
                "value": "0.800000",
            },
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "original_copy",
                "comparison_type": "baseline_original",
                "metric": "rhythm_ngram_similarity",
                "metric_parameters": json.dumps({"n": 2}, ensure_ascii=False),
                "value": "1.000000",
            },
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "original_copy",
                "comparison_type": "baseline_original",
                "metric": "ioi_similarity",
                "metric_parameters": "{}",
                "value": "1.000000",
            },
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "original_copy",
                "comparison_type": "baseline_original",
                "metric": "rhythmic_edit_distance",
                "metric_parameters": "{}",
                "value": "1.000000",
            },
        ],
    }.items():
        modality_root = metrics_root / modality
        modality_root.mkdir(parents=True, exist_ok=True)
        with (modality_root / f"{modality}_similarity_metrics.csv").open(
            "w",
            encoding="utf-8",
            newline="",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "song_id",
                    "segment_id",
                    "transformation",
                    "comparison_type",
                    "metric",
                    "metric_parameters",
                    "value",
                ],
            )
            writer.writeheader()
            writer.writerows(rows)

    return metrics_root


class GlobalMetricsTestCase(unittest.TestCase):
    def test_simple_average_for_identical_scores(self) -> None:
        metric = SimpleAverageMetric()

        value = metric.compute(
            melody_scores={"a": 1.0, "b": 1.0},
            harmony_scores={"c": 1.0},
            rhythm_scores={"d": 1.0, "e": 1.0},
        )

        self.assertEqual(value, 1.0)

    def test_simple_average_for_different_scores(self) -> None:
        metric = SimpleAverageMetric()

        value = metric.compute(
            melody_scores={"a": 1.0, "b": 0.5},
            harmony_scores={"c": 0.75},
            rhythm_scores={"d": 0.25, "e": 0.0},
        )

        self.assertAlmostEqual(value, 0.5)

    def test_weighted_average_with_valid_weights(self) -> None:
        metric = WeightedAverageMetric()

        value = metric.compute(
            melody_scores={"a": 1.0, "b": 1.0},
            harmony_scores={"c": 0.5},
            rhythm_scores={"d": 0.25},
            weights={"melody": 0.4, "harmony": 0.35, "rhythm": 0.25},
        )

        self.assertAlmostEqual(value, 0.6375)

    def test_weighted_average_rejects_invalid_weights_sum(self) -> None:
        metric = WeightedAverageMetric()

        with self.assertRaises(ValueError):
            metric.compute(
                melody_scores={"a": 1.0},
                harmony_scores={"c": 1.0},
                rhythm_scores={"d": 1.0},
                weights={"melody": 0.5, "harmony": 0.3, "rhythm": 0.3},
            )

    def test_weighted_average_rejects_negative_weights(self) -> None:
        metric = WeightedAverageMetric()

        with self.assertRaises(ValueError):
            metric.compute(
                melody_scores={"a": 1.0},
                harmony_scores={"c": 1.0},
                rhythm_scores={"d": 1.0},
                weights={"melody": 0.5, "harmony": -0.2, "rhythm": 0.7},
            )

    def test_weighted_average_for_identical_scores(self) -> None:
        metric = WeightedAverageMetric()

        value = metric.compute(
            melody_scores={"a": 1.0},
            harmony_scores={"c": 1.0},
            rhythm_scores={"d": 1.0},
            weights={"melody": 0.4, "harmony": 0.35, "rhythm": 0.25},
        )

        self.assertEqual(value, 1.0)

    def test_weighted_average_for_different_scores(self) -> None:
        metric = WeightedAverageMetric()

        value = metric.compute(
            melody_scores={"a": 1.0},
            harmony_scores={"c": 0.5},
            rhythm_scores={"d": 0.0},
            weights={"melody": 0.4, "harmony": 0.35, "rhythm": 0.25},
        )

        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_weighted_average_rejects_missing_weights(self) -> None:
        metric = WeightedAverageMetric()

        with self.assertRaises(ValueError):
            metric.compute(
                melody_scores={"a": 1.0},
                harmony_scores={"c": 1.0},
                rhythm_scores={"d": 1.0},
                weights={"melody": 0.5, "harmony": 0.5},
            )


class ComputeGlobalMetricsPipelineTestCase(unittest.TestCase):
    def test_compute_global_metrics_creates_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            metrics_root = _create_metrics_fixture(root)
            output_root = root / "data" / "results" / "compute_metrics"

            result = compute_global_metrics(
                metrics_path=metrics_root,
                output_path=output_root,
                weights={"melody": 0.4, "harmony": 0.35, "rhythm": 0.25},
            )

            self.assertEqual(result, output_root / "global")
            csv_path = output_root / "global" / "global_similarity_metrics.csv"
            self.assertTrue(csv_path.exists())
            with csv_path.open("r", encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(len(rows), 2)
            self.assertEqual({row["comparison_type"] for row in rows}, {
                "transformed",
                "baseline_original",
            })
            transformed_row = next(
                row for row in rows if row["comparison_type"] == "transformed"
            )
            self.assertEqual(transformed_row["simple_average"], "0.850000")
            self.assertEqual(transformed_row["weighted_average"], "0.857500")
            self.assertEqual(transformed_row["score_global_final"], "0.857500")

    def test_compute_global_metrics_reuses_existing_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            metrics_root = _create_metrics_fixture(root)
            output_root = root / "data" / "results" / "compute_metrics"

            compute_global_metrics(
                metrics_path=metrics_root,
                output_path=output_root,
                weights={"melody": 0.4, "harmony": 0.35, "rhythm": 0.25},
            )

            with patch(
                "experiment.16_compute_global_metrics.SimpleAverageMetric.compute"
            ) as mocked_simple, patch(
                "experiment.16_compute_global_metrics.WeightedAverageMetric.compute"
            ) as mocked_weighted:
                compute_global_metrics(
                    metrics_path=metrics_root,
                    output_path=output_root,
                    weights={"melody": 0.4, "harmony": 0.35, "rhythm": 0.25},
                )

            mocked_simple.assert_not_called()
            mocked_weighted.assert_not_called()


if __name__ == "__main__":
    unittest.main()
