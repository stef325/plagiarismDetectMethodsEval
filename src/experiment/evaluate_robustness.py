"""Pipeline para avaliacao da robustez das metricas de similaridade."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import csv
import hashlib
import json
from pathlib import Path
import time
from typing import Any


@dataclass(frozen=True)
class ExperimentPairRecord:
    """Representa um par experimental carregado do JSON."""

    pair_id: str
    pair_type: str
    original_song_id: str
    original_segment_id: str
    comparison_song_id: str
    comparison_segment_id: str
    original_representation: str
    comparison_representation: str
    transformation: str | None = None
    transformation_parameters: dict[str, Any] | None = None


@dataclass(frozen=True)
class MetricRobustnessResult:
    """Resumo da robustez de uma metrica individual."""

    metric_name: str
    threshold: float
    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float
    false_negative_rate: float
    mean_similarity_drop: float


@dataclass(frozen=True)
class TransformationDropResult:
    """Resumo da queda media por transformacao."""

    transformation_name: str
    category: str
    mean_similarity_drop: float
    pair_count: int


@dataclass(frozen=True)
class RobustnessEvaluationSummary:
    """Resumo consolidado da avaliacao de robustez."""

    pairs_path: Path
    similarity_results_path: Path
    output_path: Path
    inspection_date: datetime
    execution_time_seconds: float
    total_pairs: int
    positive_pairs: int
    negative_pairs: int
    metric_count: int
    fingerprint: str


def evaluate_robustness(
    experiment_pairs_path: str | Path | None = None,
    similarity_results_path: str | Path | None = None,
    output_path: str | Path = "data/results/evaluation",
    similarity_threshold: float = 0.7,
) -> Path:
    """Avalia a robustez das metricas com base nos resultados ja calculados."""

    pairs_path = _resolve_experiment_pairs_path(experiment_pairs_path)
    results_path = _resolve_similarity_results_path(similarity_results_path)
    output_root = Path(output_path)
    inspection_date = datetime.now()
    start_time = time.perf_counter()

    if not pairs_path.is_file():
        raise FileNotFoundError(
            f"Arquivo de pares experimentais nao encontrado: {pairs_path}"
        )
    if not results_path.is_file():
        raise FileNotFoundError(
            f"Arquivo de resultados de similaridade nao encontrado: {results_path}"
        )
    if not 0.0 <= similarity_threshold <= 1.0:
        raise ValueError(
            "O threshold de similaridade deve estar no intervalo entre 0 e 1."
        )

    output_root.mkdir(parents=True, exist_ok=True)
    csv_path = output_root / "robustness_metrics.csv"
    json_path = output_root / "robustness_metrics.json"
    report_path = output_root / "robustness_report.md"
    cache_path = output_root / "robustness_metrics_cache.json"

    fingerprint = _compute_fingerprint(
        pairs_path=pairs_path,
        results_path=results_path,
        similarity_threshold=similarity_threshold,
    )

    if _is_cache_valid(cache_path, csv_path, json_path, report_path, fingerprint):
        _print_cache_summary(cache_path, csv_path, json_path, report_path)
        return output_root

    print("Iniciando a avaliacao de robustez das metricas...")

    pair_records = _load_pairs(pairs_path)
    result_rows = _load_similarity_rows(results_path)
    rows_by_pair_id = {row["pair_id"]: row for row in result_rows}

    missing_pair_ids = sorted(
        pair.pair_id for pair in pair_records if pair.pair_id not in rows_by_pair_id
    )
    if missing_pair_ids:
        raise ValueError(
            "Alguns pares experimentais nao possuem resultados de similaridade: "
            + ", ".join(missing_pair_ids[:10])
        )

    metric_names = _metric_names_from_row(result_rows[0]) if result_rows else []
    metric_results: list[MetricRobustnessResult] = []
    csv_rows: list[dict[str, str]] = []

    for metric_name in metric_names:
        scores = [
            (
                pair.pair_type,
                float(rows_by_pair_id[pair.pair_id][metric_name]),
                pair.transformation or _infer_transformation_name(pair.comparison_representation),
                _infer_transformation_category(pair.comparison_representation),
            )
            for pair in pair_records
        ]
        confusion = _calculate_confusion_matrix(
            y_true=[score[0] == "positive" for score in scores],
            y_pred=[score[1] >= similarity_threshold for score in scores],
        )
        drops = [1.0 - score for pair_type, score, _, _ in scores if pair_type == "positive"]
        metric_result = MetricRobustnessResult(
            metric_name=metric_name,
            threshold=similarity_threshold,
            true_positives=confusion.true_positives,
            true_negatives=confusion.true_negatives,
            false_positives=confusion.false_positives,
            false_negatives=confusion.false_negatives,
            precision=_precision(confusion),
            recall=_recall(confusion),
            f1_score=_f1_score(confusion),
            false_negative_rate=_false_negative_rate(confusion),
            mean_similarity_drop=_mean(drops),
        )
        metric_results.append(metric_result)
        csv_rows.append(
            {
                "record_type": "metric_summary",
                "metric_name": metric_result.metric_name,
                "threshold": f"{metric_result.threshold:.6f}",
                "true_positives": str(metric_result.true_positives),
                "true_negatives": str(metric_result.true_negatives),
                "false_positives": str(metric_result.false_positives),
                "false_negatives": str(metric_result.false_negatives),
                "precision": f"{metric_result.precision:.6f}",
                "recall": f"{metric_result.recall:.6f}",
                "f1_score": f"{metric_result.f1_score:.6f}",
                "false_negative_rate": f"{metric_result.false_negative_rate:.6f}",
                "mean_similarity_drop": f"{metric_result.mean_similarity_drop:.6f}",
                "transformation_name": "",
                "category": "",
                "pair_count": "",
            }
        )

    transformation_drop_results = _build_transformation_drop_results(
        pair_records=pair_records,
        rows_by_pair_id=rows_by_pair_id,
        metric_names=metric_names,
    )

    for drop_result in transformation_drop_results:
        csv_rows.append(
            {
                "record_type": "transformation_drop",
                "metric_name": "",
                "threshold": f"{similarity_threshold:.6f}",
                "true_positives": "",
                "true_negatives": "",
                "false_positives": "",
                "false_negatives": "",
                "precision": "",
                "recall": "",
                "f1_score": "",
                "false_negative_rate": "",
                "mean_similarity_drop": f"{drop_result.mean_similarity_drop:.6f}",
                "transformation_name": drop_result.transformation_name,
                "category": drop_result.category,
                "pair_count": str(drop_result.pair_count),
            }
        )

    _write_csv(csv_path, csv_rows)

    positive_pairs = sum(1 for pair in pair_records if pair.pair_type == "positive")
    negative_pairs = sum(1 for pair in pair_records if pair.pair_type == "negative")
    summary = RobustnessEvaluationSummary(
        pairs_path=pairs_path,
        similarity_results_path=results_path,
        output_path=output_root,
        inspection_date=inspection_date,
        execution_time_seconds=time.perf_counter() - start_time,
        total_pairs=len(pair_records),
        positive_pairs=positive_pairs,
        negative_pairs=negative_pairs,
        metric_count=len(metric_results),
        fingerprint=fingerprint,
    )
    payload = {
        "pairs_path": pairs_path.as_posix(),
        "similarity_results_path": results_path.as_posix(),
        "threshold": similarity_threshold,
        "generated_at": inspection_date.isoformat(),
        "fingerprint": fingerprint,
        "summary": {
            "total_pairs": summary.total_pairs,
            "positive_pairs": summary.positive_pairs,
            "negative_pairs": summary.negative_pairs,
            "metric_count": summary.metric_count,
            "execution_time_seconds": summary.execution_time_seconds,
        },
        "metrics": [result.__dict__ for result in metric_results],
        "transformation_drops": [result.__dict__ for result in transformation_drop_results],
    }
    _write_json(json_path, payload)
    _write_report(report_path, summary, metric_results, transformation_drop_results, similarity_threshold)
    _write_cache(
        cache_path=cache_path,
        fingerprint=fingerprint,
        csv_path=csv_path,
        json_path=json_path,
        report_path=report_path,
        threshold=similarity_threshold,
        total_pairs=len(pair_records),
        positive_pairs=positive_pairs,
        negative_pairs=negative_pairs,
    )
    _print_summary(summary, report_path, metric_results, transformation_drop_results)
    return output_root


def _resolve_experiment_pairs_path(experiment_pairs_path: str | Path | None) -> Path:
    """Resolve o arquivo de pares experimentais."""

    candidates = _candidate_experiment_pairs_paths(experiment_pairs_path)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return candidates[0]


def _candidate_experiment_pairs_paths(
    experiment_pairs_path: str | Path | None,
) -> list[Path]:
    """Gera candidatos para localizar os pares experimentais."""

    default_root = Path("data/results/experiment")
    default_candidates = [
        default_root / "pairs" / "experiment_pairs.json",
        default_root / "experiment_pairs.json",
    ]
    if experiment_pairs_path is None:
        return default_candidates

    path = Path(experiment_pairs_path)
    if path.is_file():
        return [path, path.parent / "experiment_pairs.json", path.parent / "pairs" / "experiment_pairs.json"]
    if path.is_dir():
        return [
            path / "experiment_pairs.json",
            path / "pairs" / "experiment_pairs.json",
            path.parent / "experiment_pairs.json",
            path.parent / "pairs" / "experiment_pairs.json",
        ]
    if path.suffix.lower() == ".json":
        return [
            path,
            path.parent / "experiment_pairs.json",
            path.parent / "pairs" / "experiment_pairs.json",
            *default_candidates,
        ]
    return [
        path / "experiment_pairs.json",
        path / "pairs" / "experiment_pairs.json",
        *default_candidates,
    ]


def _resolve_similarity_results_path(similarity_results_path: str | Path | None) -> Path:
    """Resolve o arquivo de resultados de similaridade."""

    candidates = _candidate_similarity_results_paths(similarity_results_path)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return candidates[0]


def _candidate_similarity_results_paths(
    similarity_results_path: str | Path | None,
) -> list[Path]:
    """Gera candidatos para localizar os resultados de similaridade."""

    default_root = Path("data/results/experiment")
    default_candidates = [
        default_root / "similarity_results.csv",
        Path("data/results/similarity_results.csv"),
    ]
    if similarity_results_path is None:
        return default_candidates

    path = Path(similarity_results_path)
    if path.is_file():
        return [path, path.parent / "similarity_results.csv"]
    if path.is_dir():
        return [
            path / "similarity_results.csv",
            path.parent / "similarity_results.csv",
            *default_candidates,
        ]
    if path.suffix.lower() == ".csv":
        return [
            path,
            path.parent / "similarity_results.csv",
            *default_candidates,
        ]
    return [
        path / "similarity_results.csv",
        *default_candidates,
    ]


def _load_pairs(pairs_path: Path) -> list[ExperimentPairRecord]:
    """Carrega os pares experimentais do JSON."""

    payload = json.loads(pairs_path.read_text(encoding="utf-8"))
    pairs = []
    for pair in payload.get("pairs", []):
        pairs.append(
            ExperimentPairRecord(
                pair_id=str(pair["pair_id"]),
                pair_type=str(pair["pair_type"]),
                original_song_id=str(pair["original_song_id"]),
                original_segment_id=str(pair["original_segment_id"]),
                comparison_song_id=str(pair["comparison_song_id"]),
                comparison_segment_id=str(pair["comparison_segment_id"]),
                original_representation=str(pair["original_representation"]),
                comparison_representation=str(pair["comparison_representation"]),
                transformation=str(pair.get("transformation", "")) or None,
                transformation_parameters=_load_json_field(
                    pair.get("transformation_parameters", {})
                ),
            )
        )
    return pairs


def _load_similarity_rows(results_path: Path) -> list[dict[str, str]]:
    """Carrega o CSV de resultados de similaridade."""

    with results_path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _metric_names_from_row(row: dict[str, str]) -> list[str]:
    """Extrai os nomes das metricas a partir do CSV consolidado."""

    return [
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


def _calculate_confusion_matrix(
    y_true: list[bool],
    y_pred: list[bool],
) -> "_ConfusionMatrix":
    """Calcula a matriz de confusao binaria."""

    if len(y_true) != len(y_pred):
        raise ValueError("As listas de verdade e predicao devem ter o mesmo tamanho.")

    true_positives = sum(1 for truth, pred in zip(y_true, y_pred) if truth and pred)
    true_negatives = sum(1 for truth, pred in zip(y_true, y_pred) if not truth and not pred)
    false_positives = sum(1 for truth, pred in zip(y_true, y_pred) if not truth and pred)
    false_negatives = sum(1 for truth, pred in zip(y_true, y_pred) if truth and not pred)
    return _ConfusionMatrix(
        true_positives=true_positives,
        true_negatives=true_negatives,
        false_positives=false_positives,
        false_negatives=false_negatives,
    )


@dataclass(frozen=True)
class _ConfusionMatrix:
    """Matriz de confusao para classificacao binaria."""

    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int


def _precision(confusion: _ConfusionMatrix) -> float:
    """Calcula a precision."""

    denominator = confusion.true_positives + confusion.false_positives
    if denominator == 0:
        return 0.0
    return confusion.true_positives / denominator


def _recall(confusion: _ConfusionMatrix) -> float:
    """Calcula o recall."""

    denominator = confusion.true_positives + confusion.false_negatives
    if denominator == 0:
        return 0.0
    return confusion.true_positives / denominator


def _f1_score(confusion: _ConfusionMatrix) -> float:
    """Calcula o F1-score."""

    precision = _precision(confusion)
    recall = _recall(confusion)
    denominator = precision + recall
    if denominator == 0:
        return 0.0
    return 2 * precision * recall / denominator


def _false_negative_rate(confusion: _ConfusionMatrix) -> float:
    """Calcula a taxa de falso negativo."""

    denominator = confusion.false_negatives + confusion.true_positives
    if denominator == 0:
        return 0.0
    return confusion.false_negatives / denominator


def _build_transformation_drop_results(
    pair_records: list[ExperimentPairRecord],
    rows_by_pair_id: dict[str, dict[str, str]],
    metric_names: list[str],
) -> list[TransformationDropResult]:
    """Calcula a queda media por transformacao e por categoria."""

    per_transformation: dict[str, list[float]] = {}
    per_transformation_pairs: dict[str, set[str]] = {}
    per_category: dict[str, list[float]] = {}
    per_category_pairs: dict[str, set[str]] = {}

    for pair in pair_records:
        if pair.pair_type != "positive":
            continue
        transformation_name = pair.transformation or _infer_transformation_name(
            pair.comparison_representation
        )
        category = _infer_transformation_category(pair.comparison_representation)
        row = rows_by_pair_id[pair.pair_id]
        for metric_name in metric_names:
            if metric_name not in row:
                continue
            similarity_value = float(row[metric_name])
            drop_value = 1.0 - similarity_value
            per_transformation.setdefault(transformation_name, []).append(drop_value)
            per_transformation_pairs.setdefault(transformation_name, set()).add(pair.pair_id)
            per_category.setdefault(category, []).append(drop_value)
            per_category_pairs.setdefault(category, set()).add(pair.pair_id)

    results = [
        TransformationDropResult(
            transformation_name=transformation_name,
            category=_infer_category_from_transformation_name(transformation_name),
            mean_similarity_drop=_mean(values),
            pair_count=len(per_transformation_pairs.get(transformation_name, set())),
        )
        for transformation_name, values in sorted(per_transformation.items())
    ]
    results.extend(
        TransformationDropResult(
            transformation_name=category,
            category=category,
            mean_similarity_drop=_mean(values),
            pair_count=len(per_category_pairs.get(category, set())),
        )
        for category, values in sorted(per_category.items())
    )
    return results


def _infer_transformation_name(representation_path: str) -> str:
    """Infere o nome da transformacao a partir do caminho da representacao."""

    path = Path(representation_path)
    if "transformations" not in path.parts:
        return "original_copy"
    index = path.parts.index("transformations")
    if len(path.parts) <= index + 2:
        return "unknown"
    category = path.parts[index + 1]
    if category == "combined" and len(path.parts) > index + 2:
        return path.parts[index + 2]
    return path.parts[index + 2]


def _infer_transformation_category(representation_path: str) -> str:
    """Infere a categoria da transformacao a partir do caminho."""

    path = Path(representation_path)
    if "transformations" not in path.parts:
        return "Original"
    index = path.parts.index("transformations")
    if len(path.parts) <= index + 1:
        return "Desconhecida"
    category = path.parts[index + 1]
    category_map = {
        "melody": "Melodia",
        "harmony": "Harmonia",
        "rhythm": "Ritmo",
        "combined": "Transformacoes combinadas",
    }
    return category_map.get(category, "Desconhecida")


def _infer_category_from_transformation_name(transformation_name: str) -> str:
    """Converte o nome da transformacao para uma categoria amigavel."""

    if transformation_name in {"transpose", "interval_modification", "ornamentation", "simplification"}:
        return "Melodia"
    if transformation_name in {"chord_substitution", "reharmonization"}:
        return "Harmonia"
    if transformation_name in {"tempo_change", "duration_scaling", "partial_rhythm_modification"}:
        return "Ritmo"
    if transformation_name in {
        "melody_harmony",
        "melody_rhythm",
        "harmony_rhythm",
        "melody_harmony_rhythm",
    }:
        return "Transformacoes combinadas"
    return "Desconhecida"


def _mean(values: list[float]) -> float:
    """Calcula a media de uma lista de valores."""

    if not values:
        return 0.0
    return sum(values) / len(values)


def _load_json_field(value: Any) -> dict[str, Any]:
    """Converte um campo JSON textual em dicionario."""

    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip():
        loaded = json.loads(value)
        if isinstance(loaded, dict):
            return loaded
    return {}


def _write_csv(csv_path: Path, rows: list[dict[str, str]]) -> None:
    """Escreve o CSV consolidado da avaliacao de robustez."""

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "record_type",
        "metric_name",
        "threshold",
        "true_positives",
        "true_negatives",
        "false_positives",
        "false_negatives",
        "precision",
        "recall",
        "f1_score",
        "false_negative_rate",
        "mean_similarity_drop",
        "transformation_name",
        "category",
        "pair_count",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_json(json_path: Path, payload: dict[str, Any]) -> None:
    """Escreve o JSON consolidado da avaliacao de robustez."""

    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _write_report(
    report_path: Path,
    summary: RobustnessEvaluationSummary,
    metric_results: list[MetricRobustnessResult],
    transformation_drop_results: list[TransformationDropResult],
    similarity_threshold: float,
) -> None:
    """Escreve o relatorio Markdown da avaliacao de robustez."""

    lines = [
        "# Relatório de Robustez das Métricas",
        "",
        f"Data: {summary.inspection_date.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"Threshold utilizado: {similarity_threshold:.2f}",
        "",
        "## Resumo do experimento",
        "",
        f"- Pares positivos: {summary.positive_pairs}",
        f"- Pares negativos: {summary.negative_pairs}",
        f"- Métricas avaliadas: {summary.metric_count}",
        f"- Tempo de execução: {summary.execution_time_seconds:.3f} segundos",
        "",
        "## Métricas avaliadas",
        "",
        "| Métrica | Threshold | TP | TN | FP | FN | Precision | Recall | F1-score | FNR | Queda média |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for result in metric_results:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_markdown(result.metric_name),
                    f"{result.threshold:.2f}",
                    str(result.true_positives),
                    str(result.true_negatives),
                    str(result.false_positives),
                    str(result.false_negatives),
                    f"{result.precision:.6f}",
                    f"{result.recall:.6f}",
                    f"{result.f1_score:.6f}",
                    f"{result.false_negative_rate:.6f}",
                    f"{result.mean_similarity_drop:.6f}",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Queda média de similaridade por transformação",
            "",
            "| Transformação | Categoria | Queda média | Pares considerados |",
            "| --- | --- | --- | --- |",
        ]
    )
    for result in transformation_drop_results:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_markdown(result.transformation_name),
                    _escape_markdown(result.category),
                    f"{result.mean_similarity_drop:.6f}",
                    str(result.pair_count),
                ]
            )
            + " |"
        )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_cache(
    cache_path: Path,
    fingerprint: str,
    csv_path: Path,
    json_path: Path,
    report_path: Path,
    threshold: float,
    total_pairs: int,
    positive_pairs: int,
    negative_pairs: int,
) -> None:
    """Escreve o cache de reutilizacao dos resultados."""

    cache_path.write_text(
        json.dumps(
            {
                "fingerprint": fingerprint,
                "csv_path": csv_path.as_posix(),
                "json_path": json_path.as_posix(),
                "report_path": report_path.as_posix(),
                "threshold": threshold,
                "total_pairs": total_pairs,
                "positive_pairs": positive_pairs,
                "negative_pairs": negative_pairs,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def _is_cache_valid(
    cache_path: Path,
    csv_path: Path,
    json_path: Path,
    report_path: Path,
    fingerprint: str,
) -> bool:
    """Verifica se o cache existente ainda e valido."""

    if not cache_path.is_file() or not csv_path.is_file() or not json_path.is_file() or not report_path.is_file():
        return False
    cached_payload = json.loads(cache_path.read_text(encoding="utf-8"))
    return cached_payload.get("fingerprint") == fingerprint


def _print_cache_summary(
    cache_path: Path,
    csv_path: Path,
    json_path: Path,
    report_path: Path,
) -> None:
    """Exibe um resumo quando os resultados sao reutilizados."""

    cached_payload = json.loads(cache_path.read_text(encoding="utf-8"))
    print("Resultados de robustez reutilizados a partir do cache.")
    print(f"CSV: {csv_path.as_posix()}")
    print(f"JSON: {json_path.as_posix()}")
    print(f"Markdown: {report_path.as_posix()}")
    print(f"Threshold: {cached_payload.get('threshold', 0.0):.2f}")
    print(f"Total de pares: {cached_payload.get('total_pairs', 0)}")
    print(f"Pares positivos: {cached_payload.get('positive_pairs', 0)}")
    print(f"Pares negativos: {cached_payload.get('negative_pairs', 0)}")


def _print_summary(
    summary: RobustnessEvaluationSummary,
    report_path: Path,
    metric_results: list[MetricRobustnessResult],
    transformation_drop_results: list[TransformationDropResult],
) -> None:
    """Exibe um resumo amigavel da avaliacao de robustez."""

    print("Avaliacao de robustez concluida.")
    print(f"Pares processados: {summary.total_pairs}")
    print(f"Pares positivos: {summary.positive_pairs}")
    print(f"Pares negativos: {summary.negative_pairs}")
    print(f"Métricas avaliadas: {len(metric_results)}")
    print(f"Quedas de similaridade calculadas: {len(transformation_drop_results)}")
    print(f"Tempo de execução: {summary.execution_time_seconds:.3f} segundos")
    print(f"Relatório gerado em: {report_path.as_posix()}")


def _compute_fingerprint(
    pairs_path: Path,
    results_path: Path,
    similarity_threshold: float,
) -> str:
    """Gera uma assinatura estavel dos arquivos utilizados."""

    digest = hashlib.sha256()
    digest.update(pairs_path.read_bytes())
    digest.update(results_path.read_bytes())
    digest.update(f"{similarity_threshold:.6f}".encode("utf-8"))
    return digest.hexdigest()


def _escape_markdown(value: str) -> str:
    """Escapa barras verticais em tabelas Markdown."""

    return value.replace("|", "\\|")
