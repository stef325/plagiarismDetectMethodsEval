from __future__ import annotations

import csv
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from experiment.build_experiment_pairs import build_experiment_pairs


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _create_experiment_fixture(root: Path) -> tuple[Path, Path]:
    representations_root = root / "data" / "processed" / "representations"
    transformations_root = root / "data" / "processed" / "transformations"
    representations_root.mkdir(parents=True, exist_ok=True)

    for song_id in ("001", "002", "003", "004"):
        _write_json(
            representations_root / f"{song_id}_segment_01.json",
            {
                "segment_file": f"{song_id}_segment_01.mid",
                "melody": [{"pitch": 60, "duration": 0.5}],
                "harmony": [{"start": 0.0, "end": 1.0, "chord": "C4-E4-G4"}],
                "rhythm": [{"onset": 0.0, "duration": 0.5}],
            },
        )

    transformation_root = (
        transformations_root / "melody" / "transpose" / "semitones_2__random_seed_42"
    )
    transformation_root.mkdir(parents=True, exist_ok=True)

    _write_json(
        transformation_root / "001_segment_01.json",
        {
            "segment_file": "001_segment_01.mid",
            "melody": [{"pitch": 62, "duration": 0.5}],
            "transformation": "transpose",
            "parameters": {"semitones": 2},
        },
    )
    _write_json(
        transformation_root / "002_segment_01.json",
        {
            "segment_file": "002_segment_01.mid",
            "melody": [{"pitch": 62, "duration": 0.5}],
            "transformation": "transpose",
            "parameters": {"semitones": 2},
        },
    )

    with (transformation_root / "metadata.csv").open("w", encoding="utf-8", newline="") as file:
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
        writer.writerow(
            {
                "song_id": "002",
                "segment_id": "01",
                "transformation": "transpose",
                "parameters": json.dumps({"semitones": 2}, ensure_ascii=False),
                "source_file": "002_segment_01.json",
                "generated_file": "002_segment_01.json",
            }
        )

    return representations_root, transformations_root


def _load_csv_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def test_build_experiment_pairs_creates_balanced_pairs() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        representations_root, transformations_root = _create_experiment_fixture(root)
        output_root = root / "data" / "processed" / "experiment" / "pairs"

        result = build_experiment_pairs(
            representations_path=representations_root,
            transformations_path=transformations_root,
            output_path=output_root,
            random_seed=42,
        )

        assert result == output_root
        csv_path = output_root / "experiment_pairs.csv"
        json_path = output_root / "experiment_pairs.json"
        assert csv_path.exists()
        assert json_path.exists()

        rows = _load_csv_rows(csv_path)
        assert len(rows) == 4
        assert sum(row["pair_type"] == "positive" for row in rows) == 2
        assert sum(row["pair_type"] == "negative" for row in rows) == 2

        positive_rows = [row for row in rows if row["pair_type"] == "positive"]
        negative_rows = [row for row in rows if row["pair_type"] == "negative"]

        for row in positive_rows:
            assert row["original_song_id"] == row["comparison_song_id"]
            assert row["original_segment_id"] == row["comparison_segment_id"]
            assert row["transformation"] == "transpose"
            assert row["original_representation"].endswith(".json")
            assert row["comparison_representation"].endswith(".json")

        for row in negative_rows:
            assert row["original_song_id"] != row["comparison_song_id"]
            assert row["pair_type"] == "negative"
            assert row["transformation"] == ""

        payload = json.loads(json_path.read_text(encoding="utf-8"))
        assert payload["total_pairs"] == 4
        assert len(payload["pairs"]) == 4


def test_build_experiment_pairs_is_reproducible_with_same_seed() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        representations_root, transformations_root = _create_experiment_fixture(root)
        output_root = root / "data" / "processed" / "experiment" / "pairs"

        first_result = build_experiment_pairs(
            representations_path=representations_root,
            transformations_path=transformations_root,
            output_path=output_root,
            random_seed=42,
        )
        first_csv = (first_result / "experiment_pairs.csv").read_text(encoding="utf-8")
        first_json = (first_result / "experiment_pairs.json").read_text(encoding="utf-8")

        with patch("experiment.build_experiment_pairs._build_positive_pairs") as mocked_positive, patch(
            "experiment.build_experiment_pairs._build_negative_pairs"
        ) as mocked_negative:
            second_result = build_experiment_pairs(
                representations_path=representations_root,
                transformations_path=transformations_root,
                output_path=output_root,
                random_seed=42,
            )

        assert second_result == output_root
        assert (second_result / "experiment_pairs.csv").read_text(encoding="utf-8") == first_csv
        assert (second_result / "experiment_pairs.json").read_text(encoding="utf-8") == first_json
        mocked_positive.assert_not_called()
        mocked_negative.assert_not_called()


def test_build_experiment_pairs_generates_unique_pairs() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        representations_root, transformations_root = _create_experiment_fixture(root)
        output_root = root / "data" / "processed" / "experiment" / "pairs"

        build_experiment_pairs(
            representations_path=representations_root,
            transformations_path=transformations_root,
            output_path=output_root,
            random_seed=42,
        )

        rows = _load_csv_rows(output_root / "experiment_pairs.csv")
        pair_keys = {
            (
                row["pair_type"],
                row["original_song_id"],
                row["original_segment_id"],
                row["comparison_song_id"],
                row["comparison_segment_id"],
            )
            for row in rows
        }
        assert len(pair_keys) == len(rows)
        assert len({row["pair_id"] for row in rows}) == len(rows)


def test_build_experiment_pairs_rejects_missing_inputs() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        with pytest.raises(FileNotFoundError):
            build_experiment_pairs(
                representations_path=root / "missing_repr",
                transformations_path=root / "missing_trans",
                output_path=root / "data" / "processed" / "experiment" / "pairs",
                random_seed=42,
            )

