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

compute_harmony_metrics = import_module(
    "experiment.14_compute_harmony_metrics"
).compute_harmony_metrics
from metrics.harmony.chord_ngram_similarity import ChordNGramSimilarityMetric
from metrics.harmony.harmonic_edit_distance import HarmonicEditDistanceMetric
from metrics.harmony.pitch_class_similarity import PitchClassSimilarityMetric
from preprocessing.representation.harmony_representation import HarmonyRepresentation


def _build_harmony_representation(chords: list[str]) -> HarmonyRepresentation:
    return HarmonyRepresentation.from_dict(
        {
            "segment_file": "001_segment_01.mid",
            "harmony": [
                {"start": float(index), "end": float(index + 1), "chord": chord}
                for index, chord in enumerate(chords)
            ],
        }
    )


def _create_transformations_fixture(root: Path) -> tuple[Path, Path]:
    representations_root = root / "data" / "processed" / "representations"
    transformations_root = root / "data" / "processed" / "transformations"
    representations_root.mkdir(parents=True, exist_ok=True)

    original_payload = {
        "segment_file": "001_segment_01.mid",
        "harmony": [
            {"start": 0.0, "end": 1.0, "chord": "C4-E4-G4"},
            {"start": 1.0, "end": 2.0, "chord": "F4-A4-C5"},
            {"start": 2.0, "end": 3.0, "chord": "G4-B4-D5"},
        ],
    }
    (representations_root / "001_segment_01.json").write_text(
        json.dumps(original_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    metadata_root = transformations_root / "harmony" / "chord_substitution" / "strength_0p25"
    metadata_root.mkdir(parents=True, exist_ok=True)
    transformed_payload = {
        "segment_file": "001_segment_01.mid",
        "harmony": [
            {"start": 0.0, "end": 1.0, "chord": "Am4-C5-E5"},
            {"start": 1.0, "end": 2.0, "chord": "F4-A4-C5"},
            {"start": 2.0, "end": 3.0, "chord": "G4-B4-D5"},
        ],
        "transformation": "chord_substitution",
        "parameters": {"strength": 0.25},
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
                "transformation": "chord_substitution",
                "parameters": json.dumps({"strength": 0.25}, ensure_ascii=False),
                "source_file": "001_segment_01.json",
                "generated_file": "001_segment_01.json",
            }
        )

    return representations_root, transformations_root


class HarmonyMetricsTestCase(unittest.TestCase):
    def test_chord_ngram_similarity_for_identical_representations(self) -> None:
        original = _build_harmony_representation(["C4-E4-G4", "F4-A4-C5", "G4-B4-D5"])
        transformed = _build_harmony_representation(["C4-E4-G4", "F4-A4-C5", "G4-B4-D5"])

        value = ChordNGramSimilarityMetric().compute(original, transformed, n=2)

        self.assertEqual(value, 1.0)

    def test_chord_ngram_similarity_for_completely_different_representations(self) -> None:
        original = _build_harmony_representation(["C4-E4-G4", "F4-A4-C5", "G4-B4-D5"])
        transformed = _build_harmony_representation(["D4-F#4-A4", "E4-G#4-B4", "A4-C#5-E5"])

        value = ChordNGramSimilarityMetric().compute(original, transformed, n=2)

        self.assertEqual(value, 0.0)

    def test_chord_ngram_similarity_for_simple_chord_substitution(self) -> None:
        original = _build_harmony_representation(["C4-E4-G4", "F4-A4-C5", "G4-B4-D5"])
        transformed = _build_harmony_representation(["Am4-C5-E5", "F4-A4-C5", "G4-B4-D5"])

        value = ChordNGramSimilarityMetric().compute(original, transformed, n=2)

        self.assertGreater(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_chord_ngram_similarity_for_empty_sequences(self) -> None:
        original = _build_harmony_representation([])
        transformed = _build_harmony_representation([])

        value = ChordNGramSimilarityMetric().compute(original, transformed, n=2)

        self.assertEqual(value, 1.0)

    def test_harmonic_edit_distance_for_identical_representations(self) -> None:
        original = _build_harmony_representation(["C4-E4-G4", "F4-A4-C5", "G4-B4-D5"])
        transformed = _build_harmony_representation(["C4-E4-G4", "F4-A4-C5", "G4-B4-D5"])

        value = HarmonicEditDistanceMetric().compute(original, transformed)

        self.assertEqual(value, 1.0)

    def test_harmonic_edit_distance_for_reharmonization(self) -> None:
        original = _build_harmony_representation(["C4-E4-G4", "F4-A4-C5", "G4-B4-D5"])
        transformed = _build_harmony_representation(["Dm4-F4-A4", "Bb4-D5-F5", "C4-E4-G4"])

        value = HarmonicEditDistanceMetric().compute(original, transformed)

        self.assertGreaterEqual(value, 0.0)
        self.assertLess(value, 1.0)

    def test_harmonic_edit_distance_for_completely_different_representations(self) -> None:
        original = _build_harmony_representation(["C4-E4-G4", "F4-A4-C5", "G4-B4-D5"])
        transformed = _build_harmony_representation(["D4-F#4-A4", "E4-G#4-B4", "A4-C#5-E5"])

        value = HarmonicEditDistanceMetric().compute(original, transformed)

        self.assertEqual(value, 0.0)

    def test_harmonic_edit_distance_for_empty_sequences(self) -> None:
        original = _build_harmony_representation([])
        transformed = _build_harmony_representation([])

        value = HarmonicEditDistanceMetric().compute(original, transformed)

        self.assertEqual(value, 1.0)

    def test_pitch_class_similarity_for_identical_representations(self) -> None:
        original = _build_harmony_representation(["C4-E4-G4", "F4-A4-C5"])
        transformed = _build_harmony_representation(["C4-E4-G4", "F4-A4-C5"])

        value = PitchClassSimilarityMetric().compute(original, transformed)

        self.assertEqual(value, 1.0)

    def test_pitch_class_similarity_for_simplification(self) -> None:
        original = _build_harmony_representation(["C4-E4-G4-B4", "F4-A4-C5-E5"])
        transformed = _build_harmony_representation(["C4-E4-G4", "F4-A4-C5"])

        value = PitchClassSimilarityMetric().compute(original, transformed)

        self.assertGreater(value, 0.0)
        self.assertLess(value, 1.0)

    def test_pitch_class_similarity_for_completely_different_representations(self) -> None:
        original = _build_harmony_representation(["C4-E4-G4", "F4-A4-C5"])
        transformed = _build_harmony_representation(["D4-F#4-A4", "E4-G#4-B4"])

        value = PitchClassSimilarityMetric().compute(original, transformed)

        self.assertEqual(value, 0.0)

    def test_pitch_class_similarity_for_empty_sequences(self) -> None:
        original = _build_harmony_representation([])
        transformed = _build_harmony_representation([])

        value = PitchClassSimilarityMetric().compute(original, transformed)

        self.assertEqual(value, 1.0)


class ComputeHarmonyMetricsPipelineTestCase(unittest.TestCase):
    def test_compute_harmony_metrics_creates_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            representations_root, transformations_root = _create_transformations_fixture(root)
            output_root = root / "data" / "results" / "compute_metrics"

            result = compute_harmony_metrics(
                transformations_path=transformations_root,
                representations_path=representations_root,
                output_path=output_root,
                chord_ngram_n=2,
            )

            self.assertEqual(result, output_root / "harmony")
            csv_path = output_root / "harmony" / "harmony_similarity_metrics.csv"
            self.assertTrue(csv_path.exists())
            with csv_path.open("r", encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(len(rows), 6)
            self.assertEqual({row["metric"] for row in rows}, {
                "chord_ngram_similarity",
                "harmonic_edit_distance",
                "pitch_class_similarity",
            })
            self.assertEqual({row["comparison_type"] for row in rows}, {
                "transformed",
                "baseline_original",
            })
            baseline_rows = [row for row in rows if row["comparison_type"] == "baseline_original"]
            self.assertTrue(all(row["value"] == "1.000000" for row in baseline_rows))

    def test_compute_harmony_metrics_reuses_existing_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            representations_root, transformations_root = _create_transformations_fixture(root)
            output_root = root / "data" / "results" / "compute_metrics"

            compute_harmony_metrics(
                transformations_path=transformations_root,
                representations_path=representations_root,
                output_path=output_root,
                chord_ngram_n=2,
            )

            with patch(
                "experiment.14_compute_harmony_metrics.ChordNGramSimilarityMetric.compute"
            ) as mocked_ngram, patch(
                "experiment.14_compute_harmony_metrics.HarmonicEditDistanceMetric.compute"
            ) as mocked_edit, patch(
                "experiment.14_compute_harmony_metrics.PitchClassSimilarityMetric.compute"
            ) as mocked_pitch:
                compute_harmony_metrics(
                    transformations_path=transformations_root,
                    representations_path=representations_root,
                    output_path=output_root,
                    chord_ngram_n=2,
                )

            mocked_ngram.assert_not_called()
            mocked_edit.assert_not_called()
            mocked_pitch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
