from __future__ import annotations

import csv
import json
import tempfile
from importlib import import_module
from pathlib import Path
from unittest.mock import patch

import pytest

run_similarity_experiment = import_module(
    "experiment.19_run_similarity_experiment"
).run_similarity_experiment


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_combined_payload(
    segment_file: str,
    melody: list[tuple[int, float]],
    harmony: list[str],
    rhythm: list[tuple[float, float]],
) -> dict[str, object]:
    return {
        "segment_file": segment_file,
        "melody": [
            {"pitch": pitch, "duration": duration}
            for pitch, duration in melody
        ],
        "harmony": [
            {"start": float(index), "end": float(index + 1), "chord": chord}
            for index, chord in enumerate(harmony)
        ],
        "rhythm": [
            {"onset": onset, "duration": duration}
            for onset, duration in rhythm
        ],
    }


def _create_similarity_fixture(root: Path, pair_count: int = 2) -> tuple[Path, Path]:
    representations_root = root / "data" / "processed" / "representations"
    experiment_root = root / "data" / "results" / "experiment"
    representations_root.mkdir(parents=True, exist_ok=True)
    experiment_root.mkdir(parents=True, exist_ok=True)

    original_a = representations_root / "001_segment_01.json"
    comparison_a = representations_root / "001_segment_01_transpose.json"
    original_b = representations_root / "002_segment_01.json"
    comparison_b = representations_root / "152_segment_03.json"

    _write_json(
        original_a,
        _build_combined_payload(
            "001_segment_01.mid",
            melody=[(60, 0.5), (62, 0.5), (64, 0.5)],
            harmony=["C4-E4-G4", "F4-A4-C5", "G4-B4-D5"],
            rhythm=[(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)],
        ),
    )
    _write_json(
        comparison_a,
        _build_combined_payload(
            "001_segment_01.mid",
            melody=[(62, 0.5), (64, 0.5), (66, 0.5)],
            harmony=["C4-E4-G4", "F4-A4-C5", "G4-B4-D5"],
            rhythm=[(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)],
        ),
    )
    _write_json(
        original_b,
        _build_combined_payload(
            "002_segment_01.mid",
            melody=[(67, 0.5), (65, 0.5), (64, 0.5)],
            harmony=["Am4-C5-E5", "Dm4-F4-A4", "E4-G#4-B4"],
            rhythm=[(0.0, 0.25), (0.25, 0.25), (0.5, 0.5)],
        ),
    )
    _write_json(
        comparison_b,
        _build_combined_payload(
            "152_segment_03.mid",
            melody=[(72, 0.25), (71, 0.5), (69, 0.25)],
            harmony=["D4-F#4-A4", "G4-B4-D5", "C4-E4-G4"],
            rhythm=[(0.0, 0.5), (0.5, 0.25), (0.75, 0.25)],
        ),
    )

    pairs = [
        {
            "pair_id": "pair_000001",
            "pair_type": "positive",
            "original_song_id": "001",
            "original_segment_id": "01",
            "comparison_song_id": "001",
            "comparison_segment_id": "01",
            "original_representation": original_a.as_posix(),
            "comparison_representation": comparison_a.as_posix(),
            "transformation": "transpose",
            "transformation_parameters": {"semitones": 2},
        }
    ]
    if pair_count > 1:
        pairs.append(
            {
                "pair_id": "pair_000002",
                "pair_type": "negative",
                "original_song_id": "002",
                "original_segment_id": "01",
                "comparison_song_id": "152",
                "comparison_segment_id": "03",
                "original_representation": original_b.as_posix(),
                "comparison_representation": comparison_b.as_posix(),
                "transformation": None,
                "transformation_parameters": None,
            }
        )

    _write_json(
        experiment_root / "experiment_pairs.json",
        {
            "seed": 42,
            "generated_at": "2026-07-07T18:00:00",
            "pairs": pairs,
        },
    )

    return representations_root, experiment_root


def _load_csv_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def test_run_similarity_experiment_single_pair() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _, experiment_root = _create_similarity_fixture(root, pair_count=1)
        output_root = root / "data" / "results" / "experiment"

        result = run_similarity_experiment(
            experiment_pairs_path=experiment_root / "experiment_pairs.json",
            output_path=output_root,
            interval_ngram_n=2,
            chord_ngram_n=2,
            rhythm_ngram_n=2,
            global_weights={"melody": 0.4, "harmony": 0.35, "rhythm": 0.25},
        )

        assert result == output_root
        csv_path = output_root / "similarity_results.csv"
        json_path = output_root / "similarity_results.json"
        assert csv_path.exists()
        assert json_path.exists()

        rows = _load_csv_rows(csv_path)
        assert len(rows) == 1
        row = rows[0]
        assert row["pair_type"] == "positive"
        assert row["transformation"] == "transpose"
        assert row["simple_average"] == "1.000000"
        assert row["weighted_average"] == "1.000000"
        assert row["interval_ngram_similarity"] == "1.000000"
        assert row["lcs_similarity"] == "1.000000"
        assert row["edit_distance_similarity"] == "1.000000"
        assert row["chord_ngram_similarity"] == "1.000000"
        assert row["harmonic_edit_distance"] == "1.000000"
        assert row["pitch_class_similarity"] == "1.000000"
        assert row["rhythm_ngram_similarity"] == "1.000000"
        assert row["ioi_similarity"] == "1.000000"
        assert row["rhythmic_edit_distance"] == "1.000000"


def test_run_similarity_experiment_multiple_pairs() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _, experiment_root = _create_similarity_fixture(root, pair_count=2)
        output_root = root / "data" / "results" / "experiment"

        run_similarity_experiment(
            experiment_pairs_path=experiment_root / "experiment_pairs.json",
            output_path=output_root,
            interval_ngram_n=2,
            chord_ngram_n=2,
            rhythm_ngram_n=2,
            global_weights={"melody": 0.4, "harmony": 0.35, "rhythm": 0.25},
        )

        rows = _load_csv_rows(output_root / "similarity_results.csv")
        assert len(rows) == 2
        assert {row["pair_type"] for row in rows} == {"positive", "negative"}
        negative_row = next(row for row in rows if row["pair_type"] == "negative")
        assert 0.0 <= float(negative_row["simple_average"]) <= 1.0
        assert 0.0 <= float(negative_row["weighted_average"]) <= 1.0


def test_run_similarity_experiment_raises_for_missing_representations() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        experiment_root = root / "data" / "results" / "experiment"
        experiment_root.mkdir(parents=True, exist_ok=True)
        _write_json(
            experiment_root / "experiment_pairs.json",
            {
                "seed": 42,
                "pairs": [
                    {
                        "pair_id": "pair_000001",
                        "pair_type": "positive",
                        "original_song_id": "001",
                        "original_segment_id": "01",
                        "comparison_song_id": "001",
                        "comparison_segment_id": "01",
                        "original_representation": (root / "missing_original.json").as_posix(),
                        "comparison_representation": (root / "missing_comparison.json").as_posix(),
                        "transformation": "transpose",
                        "transformation_parameters": {"semitones": 2},
                    }
                ],
            },
        )

        with pytest.raises(FileNotFoundError):
            run_similarity_experiment(
                experiment_pairs_path=experiment_root / "experiment_pairs.json",
                output_path=experiment_root,
                interval_ngram_n=2,
                chord_ngram_n=2,
                rhythm_ngram_n=2,
                global_weights={"melody": 0.4, "harmony": 0.35, "rhythm": 0.25},
            )


def test_run_similarity_experiment_reuses_existing_results() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _, experiment_root = _create_similarity_fixture(root, pair_count=2)
        output_root = root / "data" / "results" / "experiment"

        run_similarity_experiment(
            experiment_pairs_path=experiment_root / "experiment_pairs.json",
            output_path=output_root,
            interval_ngram_n=2,
            chord_ngram_n=2,
            rhythm_ngram_n=2,
            global_weights={"melody": 0.4, "harmony": 0.35, "rhythm": 0.25},
        )

        with patch(
            "experiment.19_run_similarity_experiment.IntervalNGramSimilarityMetric.compute"
        ) as mocked_interval, patch(
            "experiment.19_run_similarity_experiment.LongestCommonSubsequenceMetric.compute"
        ) as mocked_lcs, patch(
            "experiment.19_run_similarity_experiment.EditDistanceMetric.compute"
        ) as mocked_edit, patch(
            "experiment.19_run_similarity_experiment.ChordNGramSimilarityMetric.compute"
        ) as mocked_chord, patch(
            "experiment.19_run_similarity_experiment.HarmonicEditDistanceMetric.compute"
        ) as mocked_harmonic_edit, patch(
            "experiment.19_run_similarity_experiment.PitchClassSimilarityMetric.compute"
        ) as mocked_pitch, patch(
            "experiment.19_run_similarity_experiment.RhythmNGramSimilarityMetric.compute"
        ) as mocked_rhythm_ngram, patch(
            "experiment.19_run_similarity_experiment.IoISimilarityMetric.compute"
        ) as mocked_ioi, patch(
            "experiment.19_run_similarity_experiment.RhythmicEditDistanceMetric.compute"
        ) as mocked_rhythm_edit, patch(
            "experiment.19_run_similarity_experiment.SimpleAverageMetric.compute"
        ) as mocked_simple, patch(
            "experiment.19_run_similarity_experiment.WeightedAverageMetric.compute"
        ) as mocked_weighted:
            run_similarity_experiment(
                experiment_pairs_path=experiment_root / "experiment_pairs.json",
                output_path=output_root,
                interval_ngram_n=2,
                chord_ngram_n=2,
                rhythm_ngram_n=2,
                global_weights={"melody": 0.4, "harmony": 0.35, "rhythm": 0.25},
            )

        mocked_interval.assert_not_called()
        mocked_lcs.assert_not_called()
        mocked_edit.assert_not_called()
        mocked_chord.assert_not_called()
        mocked_harmonic_edit.assert_not_called()
        mocked_pitch.assert_not_called()
        mocked_rhythm_ngram.assert_not_called()
        mocked_ioi.assert_not_called()
        mocked_rhythm_edit.assert_not_called()
        mocked_simple.assert_not_called()
        mocked_weighted.assert_not_called()
