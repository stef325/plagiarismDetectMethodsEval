"""Testes para o pipeline de avaliacao da robustez."""

from __future__ import annotations

from pathlib import Path
import csv
import json
from importlib import import_module

import pytest

evaluate_robustness_module = import_module("experiment.20_evaluate_robustness")
_build_transformation_drop_results = (
    evaluate_robustness_module._build_transformation_drop_results
)
_calculate_confusion_matrix = evaluate_robustness_module._calculate_confusion_matrix
_false_negative_rate = evaluate_robustness_module._false_negative_rate
_f1_score = evaluate_robustness_module._f1_score
_precision = evaluate_robustness_module._precision
_recall = evaluate_robustness_module._recall
evaluate_robustness = evaluate_robustness_module.evaluate_robustness


METRIC_NAMES = [
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


def test_calculate_confusion_matrix_counts_are_correct() -> None:
    """Confirma o calculo da matriz de confusao."""

    confusion = _calculate_confusion_matrix(
        y_true=[True, True, False, False],
        y_pred=[True, False, True, False],
    )

    assert confusion.true_positives == 1
    assert confusion.true_negatives == 1
    assert confusion.false_positives == 1
    assert confusion.false_negatives == 1


def test_classification_metrics_are_correct() -> None:
    """Confirma precision, recall, F1 e FNR."""

    confusion = _calculate_confusion_matrix(
        y_true=[True, True, False, False],
        y_pred=[True, False, True, False],
    )

    assert _precision(confusion) == 0.5
    assert _recall(confusion) == 0.5
    assert _f1_score(confusion) == 0.5
    assert _false_negative_rate(confusion) == 0.5


def test_similarity_drop_is_grouped_by_transformation_and_category() -> None:
    """Confirma a queda media por transformacao e por categoria."""

    pair_records = [
        _pair_record(
            pair_id="pair_1",
            pair_type="positive",
            comparison_representation="data/processed/transformations/melody/transpose/random_seed_42__semitones_2/001_segment_01.json",
        ),
        _pair_record(
            pair_id="pair_2",
            pair_type="positive",
            comparison_representation="data/processed/transformations/combined/melody_harmony_rhythm/mhr__hcs_strength_0p25__mt_semitones_2__rtc_tempo_factor_0p8/002_segment_01.json",
        ),
    ]
    rows_by_pair_id = {
        "pair_1": {metric_name: "0.800000" for metric_name in METRIC_NAMES},
        "pair_2": {metric_name: "0.600000" for metric_name in METRIC_NAMES},
    }

    results = _build_transformation_drop_results(
        pair_records=pair_records,
        rows_by_pair_id=rows_by_pair_id,
        metric_names=METRIC_NAMES,
    )

    transpose_result = next(result for result in results if result.transformation_name == "transpose")
    combined_result = next(
        result
        for result in results
        if result.transformation_name == "melody_harmony_rhythm"
    )
    melody_category = next(result for result in results if result.category == "Melodia")
    combined_category = next(
        result for result in results if result.category == "Transformacoes combinadas"
    )

    assert transpose_result.mean_similarity_drop == pytest.approx(0.2)
    assert transpose_result.pair_count == 1
    assert combined_result.mean_similarity_drop == pytest.approx(0.4)
    assert melody_category.mean_similarity_drop == pytest.approx(0.2)
    assert combined_category.mean_similarity_drop == pytest.approx(0.4)


def test_evaluate_robustness_on_balanced_dataset(tmp_path: Path) -> None:
    """Executa o pipeline sobre um conjunto balanceado."""

    pairs_path, results_path = _write_dataset(tmp_path, positive_scores=0.9, negative_scores=0.1)
    output_root = tmp_path / "evaluation"

    result = evaluate_robustness(
        experiment_pairs_path=pairs_path,
        similarity_results_path=results_path,
        output_path=output_root,
        similarity_threshold=0.7,
    )

    csv_path = result / "robustness_metrics.csv"
    json_path = result / "robustness_metrics.json"
    report_path = result / "robustness_report.md"

    assert csv_path.is_file()
    assert json_path.is_file()
    assert report_path.is_file()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["summary"]["positive_pairs"] == 2
    assert payload["summary"]["negative_pairs"] == 2
    assert len(payload["metrics"]) == 11

    metric_row = next(row for row in _read_csv(csv_path) if row["record_type"] == "metric_summary" and row["metric_name"] == "simple_average")
    assert metric_row["true_positives"] == "2"
    assert metric_row["true_negatives"] == "2"
    assert metric_row["false_positives"] == "0"
    assert metric_row["false_negatives"] == "0"
    assert metric_row["precision"] == "1.000000"
    assert metric_row["recall"] == "1.000000"
    assert metric_row["f1_score"] == "1.000000"
    assert metric_row["false_negative_rate"] == "0.000000"


def test_evaluate_robustness_respects_threshold_changes(tmp_path: Path) -> None:
    """Confirma que thresholds diferentes produzem classificacoes diferentes."""

    pairs_path, results_path = _write_dataset(tmp_path, positive_scores=0.8, negative_scores=0.6)
    low_threshold_output = tmp_path / "low"
    high_threshold_output = tmp_path / "high"

    low_result = evaluate_robustness(
        experiment_pairs_path=pairs_path,
        similarity_results_path=results_path,
        output_path=low_threshold_output,
        similarity_threshold=0.7,
    )
    high_result = evaluate_robustness(
        experiment_pairs_path=pairs_path,
        similarity_results_path=results_path,
        output_path=high_threshold_output,
        similarity_threshold=0.9,
    )

    low_metric = next(
        row
        for row in _read_csv(low_result / "robustness_metrics.csv")
        if row["record_type"] == "metric_summary" and row["metric_name"] == "simple_average"
    )
    high_metric = next(
        row
        for row in _read_csv(high_result / "robustness_metrics.csv")
        if row["record_type"] == "metric_summary" and row["metric_name"] == "simple_average"
    )

    assert low_metric["false_negatives"] == "0"
    assert high_metric["false_negatives"] == "2"
    assert low_metric["precision"] == "1.000000"
    assert high_metric["precision"] == "0.000000"


def test_evaluate_robustness_handles_only_positive_pairs(tmp_path: Path) -> None:
    """Confirma o comportamento com apenas pares positivos."""

    pairs_path, results_path = _write_dataset(
        tmp_path,
        positive_scores=0.95,
        negative_scores=None,
        positive_count=3,
        negative_count=0,
    )
    output_root = tmp_path / "positives"

    evaluate_robustness(
        experiment_pairs_path=pairs_path,
        similarity_results_path=results_path,
        output_path=output_root,
        similarity_threshold=0.7,
    )

    metric_row = next(
        row
        for row in _read_csv(output_root / "robustness_metrics.csv")
        if row["record_type"] == "metric_summary" and row["metric_name"] == "simple_average"
    )
    assert metric_row["true_positives"] == "3"
    assert metric_row["true_negatives"] == "0"
    assert metric_row["false_positives"] == "0"
    assert metric_row["false_negatives"] == "0"


def test_evaluate_robustness_handles_only_negative_pairs(tmp_path: Path) -> None:
    """Confirma o comportamento com apenas pares negativos."""

    pairs_path, results_path = _write_dataset(
        tmp_path,
        positive_scores=None,
        negative_scores=0.05,
        positive_count=0,
        negative_count=3,
    )
    output_root = tmp_path / "negatives"

    evaluate_robustness(
        experiment_pairs_path=pairs_path,
        similarity_results_path=results_path,
        output_path=output_root,
        similarity_threshold=0.7,
    )

    metric_row = next(
        row
        for row in _read_csv(output_root / "robustness_metrics.csv")
        if row["record_type"] == "metric_summary" and row["metric_name"] == "simple_average"
    )
    assert metric_row["true_positives"] == "0"
    assert metric_row["true_negatives"] == "3"
    assert metric_row["false_positives"] == "0"
    assert metric_row["false_negatives"] == "0"


def _pair_record(pair_id: str, pair_type: str, comparison_representation: str) -> object:
    """Cria um registro de par no formato esperado pelo pipeline."""

    return type(
        "PairRecord",
        (),
        {
            "pair_id": pair_id,
            "pair_type": pair_type,
            "original_song_id": "001",
            "original_segment_id": "01",
            "comparison_song_id": "001",
            "comparison_segment_id": "01",
            "original_representation": "data/processed/representations/001_segment_01.json",
            "comparison_representation": comparison_representation,
            "transformation": None,
            "transformation_parameters": None,
        },
    )()


def _write_dataset(
    tmp_path: Path,
    positive_scores: float | None,
    negative_scores: float | None,
    positive_count: int = 2,
    negative_count: int = 2,
) -> tuple[Path, Path]:
    """Escreve arquivos artificiais de pares e resultados."""

    pairs_path = tmp_path / "experiment_pairs.json"
    results_path = tmp_path / "similarity_results.csv"

    pairs: list[dict[str, object]] = []
    rows: list[dict[str, str]] = []

    for index in range(positive_count):
        pair_id = f"pair_pos_{index}"
        comparison_representation = (
            "data/processed/transformations/melody/transpose/random_seed_42__semitones_2/"
            f"001_segment_{index:02d}.json"
        )
        pairs.append(
            {
                "pair_id": pair_id,
                "pair_type": "positive",
                "original_song_id": "001",
                "original_segment_id": f"{index:02d}",
                "comparison_song_id": "001",
                "comparison_segment_id": f"{index:02d}",
                "original_representation": f"data/processed/representations/001_segment_{index:02d}.json",
                "comparison_representation": comparison_representation,
                "transformation": "transpose",
                "transformation_parameters": {"semitones": 2},
            }
        )
        rows.append(_build_similarity_row(pair_id, 0.9 if positive_scores is None else positive_scores))

    for index in range(negative_count):
        pair_id = f"pair_neg_{index}"
        pairs.append(
            {
                "pair_id": pair_id,
                "pair_type": "negative",
                "original_song_id": "001",
                "original_segment_id": f"{index:02d}",
                "comparison_song_id": "002",
                "comparison_segment_id": f"{index:02d}",
                "original_representation": f"data/processed/representations/001_segment_{index:02d}.json",
                "comparison_representation": f"data/processed/representations/002_segment_{index:02d}.json",
                "transformation": "",
                "transformation_parameters": {},
            }
        )
        rows.append(_build_similarity_row(pair_id, 0.1 if negative_scores is None else negative_scores))

    pairs_path.write_text(
        json.dumps({"pairs": pairs}, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )

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
                *METRIC_NAMES,
                "simple_average",
                "weighted_average",
                "original_representation",
                "comparison_representation",
                "weights_used",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    return pairs_path, results_path


def _build_similarity_row(pair_id: str, score: float) -> dict[str, str]:
    """Cria uma linha de resultados com um valor uniforme para todas as metricas."""

    row = {
        "pair_id": pair_id,
        "pair_type": "positive" if pair_id.startswith("pair_pos_") else "negative",
        "original_song_id": "001",
        "original_segment_id": "01",
        "comparison_song_id": "001" if pair_id.startswith("pair_pos_") else "002",
        "comparison_segment_id": "01",
        "transformation": "transpose" if pair_id.startswith("pair_pos_") else "",
        "original_representation": "data/processed/representations/001_segment_01.json",
        "comparison_representation": "data/processed/transformations/melody/transpose/random_seed_42__semitones_2/001_segment_01.json"
        if pair_id.startswith("pair_pos_")
        else "data/processed/representations/002_segment_01.json",
        "weights_used": '{"harmony": 0.35, "melody": 0.4, "rhythm": 0.25}',
    }
    for metric_name in METRIC_NAMES:
        row[metric_name] = f"{score:.6f}"
    row["simple_average"] = f"{score:.6f}"
    row["weighted_average"] = f"{score:.6f}"
    return row


def _read_csv(path: Path) -> list[dict[str, str]]:
    """Carrega um CSV para lista de dicionarios."""

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))
