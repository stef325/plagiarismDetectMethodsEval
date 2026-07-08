"""Testes para o pipeline de avaliacao da interpretabilidade."""

from __future__ import annotations

from pathlib import Path
import csv
import json

import pytest

from experiment.evaluate_interpretability import evaluate_interpretability


METRIC_COLUMNS = [
    "interval_ngram_similarity",
    "lcs_similarity",
    "edit_distance_similarity",
    "chord_ngram_similarity",
    "harmonic_edit_distance",
    "pitch_class_similarity",
    "rhythm_ngram_similarity",
    "ioi_similarity",
    "rhythmic_edit_distance",
    "simple_average",
    "weighted_average",
]


def test_evaluate_interpretability_classifies_transformed_components(tmp_path: Path) -> None:
    """Confirma a classificacao automatica dos componentes transformados."""

    dataset = _build_dataset(tmp_path)

    output_root = evaluate_interpretability(
        experiment_pairs_path=dataset["pairs_path"],
        similarity_results_path=dataset["results_path"],
        transformations_root=dataset["transformations_root"],
        output_path=tmp_path / "output",
    )

    rows = _read_csv(output_root / "interpretability_results.csv")
    melody_row = next(row for row in rows if row["pair_id"] == "pair_melody")
    harmony_row = next(row for row in rows if row["pair_id"] == "pair_harmony")
    rhythm_row = next(row for row in rows if row["pair_id"] == "pair_rhythm")
    combined_row = next(row for row in rows if row["pair_id"] == "pair_combined")
    negative_row = next(row for row in rows if row["pair_id"] == "pair_negative")

    assert melody_row["component_transformed"] == "Melodia"
    assert harmony_row["component_transformed"] == "Harmonia"
    assert rhythm_row["component_transformed"] == "Ritmo"
    assert combined_row["component_transformed"] == "Combinações"
    assert negative_row["component_transformed"] == "Não aplicável"

    assert float(melody_row["score_melody"]) < float(melody_row["score_harmony"])
    assert float(harmony_row["score_harmony"]) < float(harmony_row["score_melody"])
    assert float(rhythm_row["score_rhythm"]) < float(rhythm_row["score_melody"])
    assert float(combined_row["score_gap"]) > 0.0


def test_evaluate_interpretability_generates_statistics_and_evidence(tmp_path: Path) -> None:
    """Confirma a geracao de estatisticas e evidencias no relatorio."""

    dataset = _build_dataset(tmp_path)

    output_root = evaluate_interpretability(
        experiment_pairs_path=dataset["pairs_path"],
        similarity_results_path=dataset["results_path"],
        transformations_root=dataset["transformations_root"],
        output_path=tmp_path / "output",
    )

    json_path = output_root / "interpretability_results.json"
    report_path = output_root / "interpretability_report.md"

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert len(payload["category_stats"]) == 4
    assert len(payload["category_evidence"]) == 4
    assert payload["summary"]["positive_pairs"] == 4
    assert payload["summary"]["negative_pairs"] == 1

    report = report_path.read_text(encoding="utf-8")
    assert "Estatísticas por tipo de transformação" in report
    assert "Comparação entre métricas individuais e métrica global" in report
    assert "Evidências interpretativas" in report
    assert "Métrica mais sensível" in report
    assert "Melodia" in report
    assert "Harmonia" in report
    assert "Ritmo" in report
    assert "Combinações" in report


def test_evaluate_interpretability_reports_global_comparison(tmp_path: Path) -> None:
    """Confirma a comparação entre métricas individuais e global."""

    dataset = _build_dataset(tmp_path)

    output_root = evaluate_interpretability(
        experiment_pairs_path=dataset["pairs_path"],
        similarity_results_path=dataset["results_path"],
        transformations_root=dataset["transformations_root"],
        output_path=tmp_path / "output",
    )

    rows = _read_csv(output_root / "interpretability_results.csv")
    melody_row = next(row for row in rows if row["pair_id"] == "pair_melody")

    assert float(melody_row["simple_average"]) == pytest.approx(0.723333, rel=1e-6)
    assert float(melody_row["weighted_average"]) == pytest.approx(0.420000, rel=1e-6)
    assert float(melody_row["global_delta"]) == pytest.approx(
        float(melody_row["weighted_average"]) - float(melody_row["transformed_component_score"]),
        rel=1e-6,
    )


def test_evaluate_interpretability_reuses_cache(tmp_path: Path) -> None:
    """Confirma a reutilizacao do cache na segunda execucao."""

    dataset = _build_dataset(tmp_path)

    first_output = evaluate_interpretability(
        experiment_pairs_path=dataset["pairs_path"],
        similarity_results_path=dataset["results_path"],
        transformations_root=dataset["transformations_root"],
        output_path=tmp_path / "output",
    )
    first_report = (first_output / "interpretability_report.md").read_text(encoding="utf-8")

    second_output = evaluate_interpretability(
        experiment_pairs_path=dataset["pairs_path"],
        similarity_results_path=dataset["results_path"],
        transformations_root=dataset["transformations_root"],
        output_path=tmp_path / "output",
    )
    second_report = (second_output / "interpretability_report.md").read_text(encoding="utf-8")

    assert second_output == first_output
    assert second_report == first_report


def _build_dataset(tmp_path: Path) -> dict[str, Path]:
    """Cria um conjunto artificial de pares, metadados e resultados."""

    transformations_root = tmp_path / "data" / "processed" / "transformations"
    melody_metadata = _write_metadata(
        transformations_root
        / "melody"
        / "transpose"
        / "random_seed_42__semitones_2",
        [
            {
                "song_id": "001",
                "segment_id": "01",
                "transformation": "transpose",
                "parameters": json.dumps({"semitones": 2}, ensure_ascii=False),
                "source_file": "001_segment_01.json",
                "generated_file": "001_segment_01.json",
            }
        ],
    )
    harmony_metadata = _write_metadata(
        transformations_root
        / "harmony"
        / "chord_substitution"
        / "random_seed_42__strength_0p25",
        [
            {
                "song_id": "002",
                "segment_id": "01",
                "transformation": "chord_substitution",
                "parameters": json.dumps({"strength": 0.25}, ensure_ascii=False),
                "source_file": "002_segment_01.json",
                "generated_file": "002_segment_01.json",
            }
        ],
    )
    rhythm_metadata = _write_metadata(
        transformations_root
        / "rhythm"
        / "tempo_change"
        / "random_seed_42__tempo_factor_0p8",
        [
            {
                "song_id": "003",
                "segment_id": "01",
                "transformation": "tempo_change",
                "parameters": json.dumps({"tempo_factor": 0.8}, ensure_ascii=False),
                "source_file": "003_segment_01.json",
                "generated_file": "003_segment_01.json",
            }
        ],
    )
    combined_metadata = _write_metadata(
        transformations_root
        / "combined"
        / "melody_harmony_rhythm"
        / "mhr__hcs_strength_0p25__mt_semitones_2__rtc_tempo_factor_0p8",
        [
            {
                "song_id": "004",
                "segment_id": "01",
                "combination": "melody_harmony_rhythm",
                "individual_transformations": json.dumps(
                    {
                        "harmony": "chord_substitution",
                        "melody": "transpose",
                        "rhythm": "tempo_change",
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "parameters": json.dumps(
                    {
                        "harmony": {
                            "parameters": {"strength": 0.25},
                            "transformation": "chord_substitution",
                        },
                        "melody": {
                            "parameters": {"semitones": 2},
                            "transformation": "transpose",
                        },
                        "rhythm": {
                            "parameters": {"tempo_factor": 0.8},
                            "transformation": "tempo_change",
                        },
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "source_file": "004_segment_01.json",
                "generated_file": "004_segment_01.json",
            }
        ],
    )

    pairs_path = tmp_path / "experiment_pairs.json"
    pairs = [
        _build_pair(
            "pair_melody",
            "positive",
            "001",
            "Melodia",
            melody_metadata.parent,
            tmp_path / "data" / "processed" / "representations",
        ),
        _build_pair(
            "pair_harmony",
            "positive",
            "002",
            "Harmonia",
            harmony_metadata.parent,
            tmp_path / "data" / "processed" / "representations",
        ),
        _build_pair(
            "pair_rhythm",
            "positive",
            "003",
            "Ritmo",
            rhythm_metadata.parent,
            tmp_path / "data" / "processed" / "representations",
        ),
        _build_pair(
            "pair_combined",
            "positive",
            "004",
            "Combinações",
            combined_metadata.parent,
            tmp_path / "data" / "processed" / "representations",
        ),
        {
            "pair_id": "pair_negative",
            "pair_type": "negative",
            "original_song_id": "005",
            "original_segment_id": "01",
            "comparison_song_id": "099",
            "comparison_segment_id": "01",
            "original_representation": (tmp_path / "data" / "processed" / "representations" / "005_segment_01.json").resolve().as_posix(),
            "comparison_representation": (tmp_path / "data" / "processed" / "representations" / "099_segment_01.json").resolve().as_posix(),
            "transformation": "",
            "transformation_parameters": {},
        },
    ]
    pairs_path.write_text(
        json.dumps({"pairs": pairs}, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    results_path = tmp_path / "similarity_results.csv"
    _write_similarity_results(results_path)

    return {
        "pairs_path": pairs_path,
        "results_path": results_path,
        "transformations_root": transformations_root,
    }


def _build_pair(
    pair_id: str,
    pair_type: str,
    song_id: str,
    component_category: str,
    transformation_root: Path,
    original_representation_root: Path,
) -> dict[str, object]:
    """Cria um par positivo para o conjunto artificial."""

    comparison_path = (
        transformation_root / f"{song_id}_segment_01.json"
    ).resolve().as_posix()
    return {
        "pair_id": pair_id,
        "pair_type": pair_type,
        "original_song_id": song_id,
        "original_segment_id": "01",
        "comparison_song_id": song_id,
        "comparison_segment_id": "01",
        "original_representation": (
            original_representation_root / f"{song_id}_segment_01.json"
        ).resolve().as_posix(),
        "comparison_representation": comparison_path,
        "transformation": "",
        "transformation_parameters": {},
    }


def _write_similarity_results(results_path: Path) -> None:
    """Escreve um CSV artificial com resultados de similaridade."""

    rows = [
        _build_similarity_row(
            "pair_melody",
            "001",
            "001",
            melody=(0.25, 0.30, 0.35),
            harmony=(0.92, 0.90, 0.94),
            rhythm=(0.95, 0.96, 0.94),
            simple_average=0.723333,
            weighted_average=0.420000,
        ),
        _build_similarity_row(
            "pair_harmony",
            "002",
            "002",
            melody=(0.91, 0.92, 0.93),
            harmony=(0.20, 0.28, 0.30),
            rhythm=(0.90, 0.91, 0.89),
            simple_average=0.716667,
            weighted_average=0.410000,
        ),
        _build_similarity_row(
            "pair_rhythm",
            "003",
            "003",
            melody=(0.93, 0.94, 0.92),
            harmony=(0.90, 0.89, 0.91),
            rhythm=(0.18, 0.22, 0.20),
            simple_average=0.665556,
            weighted_average=0.380000,
        ),
        _build_similarity_row(
            "pair_combined",
            "004",
            "004",
            melody=(0.40, 0.45, 0.42),
            harmony=(0.35, 0.30, 0.32),
            rhythm=(0.38, 0.41, 0.39),
            simple_average=0.372222,
            weighted_average=0.360000,
        ),
        _build_similarity_row(
            "pair_negative",
            "005",
            "099",
            melody=(0.10, 0.12, 0.11),
            harmony=(0.09, 0.10, 0.08),
            rhythm=(0.07, 0.08, 0.09),
            simple_average=0.093333,
            weighted_average=0.090000,
            pair_type="negative",
        ),
    ]

    with results_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "pair_id",
                "pair_type",
                "original_song_id",
                "original_segment_id",
                "comparison_song_id",
                "comparison_segment_id",
                "transformation",
                *METRIC_COLUMNS[:-2],
                "simple_average",
                "weighted_average",
                "original_representation",
                "comparison_representation",
                "weights_used",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def _build_similarity_row(
    pair_id: str,
    original_song_id: str,
    comparison_song_id: str,
    melody: tuple[float, float, float],
    harmony: tuple[float, float, float],
    rhythm: tuple[float, float, float],
    simple_average: float,
    weighted_average: float,
    pair_type: str = "positive",
) -> dict[str, str]:
    """Cria uma linha de resultados de similaridade."""

    row = {
        "pair_id": pair_id,
        "pair_type": pair_type,
        "original_song_id": original_song_id,
        "original_segment_id": "01",
        "comparison_song_id": comparison_song_id,
        "comparison_segment_id": "01",
        "transformation": "",
        "original_representation": "original.json",
        "comparison_representation": "comparison.json",
        "weights_used": '{"harmony": 0.35, "melody": 0.4, "rhythm": 0.25}',
    }
    metric_values = [
        *melody,
        *harmony,
        *rhythm,
    ]
    for column, value in zip(METRIC_COLUMNS[:-2], metric_values, strict=True):
        row[column] = f"{value:.6f}"
    row["simple_average"] = f"{simple_average:.6f}"
    row["weighted_average"] = f"{weighted_average:.6f}"
    return row


def _write_metadata(metadata_root: Path, rows: list[dict[str, str]]) -> Path:
    """Escreve um CSV de metadados de transformacao."""

    metadata_root.mkdir(parents=True, exist_ok=True)
    metadata_path = metadata_root / "metadata.csv"
    with metadata_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return metadata_path


def _read_csv(path: Path) -> list[dict[str, str]]:
    """Lê um CSV para lista de dicionários."""

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))
