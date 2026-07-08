"""Testes para o pipeline de consolidacao dos resultados."""

from __future__ import annotations

from pathlib import Path
import csv
import json

from experiment.consolidate_results import consolidate_results


def test_consolidate_results_creates_expected_outputs(tmp_path: Path) -> None:
    """Confirma a geracao dos arquivos consolidados."""

    dataset = _build_dataset(tmp_path)

    output_root = consolidate_results(
        similarity_results_path=dataset["similarity_path"],
        robustness_results_path=dataset["robustness_path"],
        interpretability_results_path=dataset["interpretability_path"],
        output_path=tmp_path / "consolidated",
    )

    assert (output_root / "consolidated_similarity.csv").is_file()
    assert (output_root / "consolidated_robustness.csv").is_file()
    assert (output_root / "consolidated_interpretability.csv").is_file()
    assert (output_root / "experiment_summary.csv").is_file()
    assert (output_root / "statistics_summary.csv").is_file()
    assert (output_root / "consolidated_results.json").is_file()
    assert (output_root / "consolidated_results.md").is_file()


def test_consolidate_results_groups_by_experiment_type(tmp_path: Path) -> None:
    """Confirma o agrupamento por tipo de experimento."""

    dataset = _build_dataset(tmp_path)

    output_root = consolidate_results(
        similarity_results_path=dataset["similarity_path"],
        robustness_results_path=dataset["robustness_path"],
        interpretability_results_path=dataset["interpretability_path"],
        output_path=tmp_path / "consolidated",
    )

    rows = _read_csv(output_root / "experiment_summary.csv")
    experiments = {row["experiment"] for row in rows}
    assert experiments == {
        "Transformações Melódicas",
        "Transformações Harmônicas",
        "Transformações Rítmicas",
        "Transformações Combinadas",
    }


def test_consolidate_results_reuses_cache(tmp_path: Path) -> None:
    """Confirma a reutilizacao do cache na segunda execucao."""

    dataset = _build_dataset(tmp_path)

    first_output = consolidate_results(
        similarity_results_path=dataset["similarity_path"],
        robustness_results_path=dataset["robustness_path"],
        interpretability_results_path=dataset["interpretability_path"],
        output_path=tmp_path / "consolidated",
    )
    first_json = (first_output / "consolidated_results.json").read_text(encoding="utf-8")

    second_output = consolidate_results(
        similarity_results_path=dataset["similarity_path"],
        robustness_results_path=dataset["robustness_path"],
        interpretability_results_path=dataset["interpretability_path"],
        output_path=tmp_path / "consolidated",
    )
    second_json = (second_output / "consolidated_results.json").read_text(encoding="utf-8")

    assert second_output == first_output
    assert second_json == first_json


def _build_dataset(tmp_path: Path) -> dict[str, Path]:
    """Cria arquivos artificiais para a consolidacao."""

    similarity_path = tmp_path / "similarity_results.csv"
    robustness_path = tmp_path / "robustness_metrics.csv"
    interpretability_path = tmp_path / "interpretability_results.csv"

    similarity_rows = [
        {
            "pair_id": "pair_1",
            "pair_type": "positive",
            "transformation": "transpose",
            "score_melody": "0.900000",
            "score_harmony": "0.400000",
            "score_rhythm": "0.500000",
            "score_global": "0.600000",
            "comparison_representation": "data/processed/transformations/melody/transpose/x.json",
        },
        {
            "pair_id": "pair_2",
            "pair_type": "positive",
            "transformation": "chord_substitution",
            "score_melody": "0.300000",
            "score_harmony": "0.800000",
            "score_rhythm": "0.450000",
            "score_global": "0.550000",
            "comparison_representation": "data/processed/transformations/harmony/chord_substitution/x.json",
        },
        {
            "pair_id": "pair_3",
            "pair_type": "positive",
            "transformation": "tempo_change",
            "score_melody": "0.350000",
            "score_harmony": "0.400000",
            "score_rhythm": "0.850000",
            "score_global": "0.600000",
            "comparison_representation": "data/processed/transformations/rhythm/tempo_change/x.json",
        },
        {
            "pair_id": "pair_4",
            "pair_type": "positive",
            "transformation": "melody_harmony_rhythm",
            "score_melody": "0.250000",
            "score_harmony": "0.260000",
            "score_rhythm": "0.270000",
            "score_global": "0.260000",
            "comparison_representation": "data/processed/transformations/combined/melody_harmony_rhythm/x.json",
        },
    ]
    with similarity_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(similarity_rows[0].keys()))
        writer.writeheader()
        writer.writerows(similarity_rows)

    robustness_rows = [
        {
            "record_type": "metric_summary",
            "metric_name": "interval_ngram_similarity",
            "precision": "0.900000",
            "recall": "0.800000",
            "f1_score": "0.850000",
            "false_negative_rate": "0.200000",
        },
        {
            "record_type": "metric_summary",
            "metric_name": "lcs_similarity",
            "precision": "0.950000",
            "recall": "0.700000",
            "f1_score": "0.810000",
            "false_negative_rate": "0.300000",
        },
    ]
    with robustness_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(robustness_rows[0].keys()))
        writer.writeheader()
        writer.writerows(robustness_rows)

    interpretability_rows = [
        {
            "pair_id": "pair_1",
            "pair_type": "positive",
            "transformation": "transpose",
            "component_transformed": "Melodia",
            "score_melody": "0.900000",
            "score_harmony": "0.400000",
            "score_rhythm": "0.500000",
            "simple_average": "0.600000",
            "weighted_average": "0.620000",
            "score_global": "0.620000",
            "score_gap": "0.500000",
            "transformed_component_score": "0.900000",
            "global_delta": "-0.280000",
            "observations": "ok",
        },
        {
            "pair_id": "pair_2",
            "pair_type": "positive",
            "transformation": "chord_substitution",
            "component_transformed": "Harmonia",
            "score_melody": "0.300000",
            "score_harmony": "0.800000",
            "score_rhythm": "0.450000",
            "simple_average": "0.516667",
            "weighted_average": "0.540000",
            "score_global": "0.540000",
            "score_gap": "0.500000",
            "transformed_component_score": "0.800000",
            "global_delta": "-0.260000",
            "observations": "ok",
        },
        {
            "pair_id": "pair_3",
            "pair_type": "positive",
            "transformation": "tempo_change",
            "component_transformed": "Ritmo",
            "score_melody": "0.350000",
            "score_harmony": "0.400000",
            "score_rhythm": "0.850000",
            "simple_average": "0.533333",
            "weighted_average": "0.560000",
            "score_global": "0.560000",
            "score_gap": "0.500000",
            "transformed_component_score": "0.850000",
            "global_delta": "-0.290000",
            "observations": "ok",
        },
        {
            "pair_id": "pair_4",
            "pair_type": "positive",
            "transformation": "melody_harmony_rhythm",
            "component_transformed": "Combinações",
            "score_melody": "0.250000",
            "score_harmony": "0.260000",
            "score_rhythm": "0.270000",
            "simple_average": "0.260000",
            "weighted_average": "0.260000",
            "score_global": "0.260000",
            "score_gap": "0.020000",
            "transformed_component_score": "0.260000",
            "global_delta": "0.000000",
            "observations": "ok",
        },
    ]
    with interpretability_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(interpretability_rows[0].keys()))
        writer.writeheader()
        writer.writerows(interpretability_rows)

    return {
        "similarity_path": similarity_path,
        "robustness_path": robustness_path,
        "interpretability_path": interpretability_path,
    }


def _read_csv(path: Path) -> list[dict[str, str]]:
    """Lê um CSV para lista de dicionários."""

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))
