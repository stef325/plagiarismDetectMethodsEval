"""Pipeline para cálculo da métrica global de similaridade."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import csv
import importlib
import json
from pathlib import Path
import time
from typing import Any, Mapping

SimpleAverageMetric = importlib.import_module(
    "metrics.global.simple_average"
).SimpleAverageMetric
WeightedAverageMetric = importlib.import_module(
    "metrics.global.weighted_average"
).WeightedAverageMetric
validate_weights = importlib.import_module(
    "metrics.global._helpers"
).validate_weights


@dataclass(frozen=True)
class GlobalMetricSummary:
    """Resumo da execução da métrica global."""

    melody_metrics_path: Path
    harmony_metrics_path: Path
    rhythm_metrics_path: Path
    output_path: Path
    inspection_date: datetime
    execution_time_seconds: float
    comparisons_found: int
    metric_rows_created: int
    metric_rows_reused: int


def compute_global_metrics(
    metrics_path: str | Path,
    output_path: str | Path,
    weights: Mapping[str, float],
) -> Path:
    """Executa a métrica global a partir dos resultados já calculados."""

    metrics_root = Path(metrics_path)
    output_root = Path(output_path) / "global"
    inspection_date = datetime.now()
    start_time = time.perf_counter()
    validated_weights = validate_weights(weights)

    melody_metrics_path = metrics_root / "melody" / "melody_similarity_metrics.csv"
    harmony_metrics_path = metrics_root / "harmony" / "harmony_similarity_metrics.csv"
    rhythm_metrics_path = metrics_root / "rhythm" / "rhythm_similarity_metrics.csv"

    for path, label in (
        (melody_metrics_path, "melódicas"),
        (harmony_metrics_path, "harmônicas"),
        (rhythm_metrics_path, "rítmicas"),
    ):
        if not path.is_file():
            raise FileNotFoundError(
                f"Arquivo de métricas {label} não encontrado: {path}"
            )

    output_root.mkdir(parents=True, exist_ok=True)
    metrics_csv_path = output_root / "global_similarity_metrics.csv"

    melody_rows = _load_metric_rows(melody_metrics_path)
    harmony_rows = _load_metric_rows(harmony_metrics_path)
    rhythm_rows = _load_metric_rows(rhythm_metrics_path)

    melody_groups = _group_rows_by_comparison(melody_rows)
    harmony_groups = _group_rows_by_comparison(harmony_rows)
    rhythm_groups = _group_rows_by_comparison(rhythm_rows)

    available_keys = set(melody_groups) & set(harmony_groups) & set(rhythm_groups)
    all_keys = set(melody_groups) | set(harmony_groups) | set(rhythm_groups)
    missing_keys = sorted(all_keys - available_keys)

    existing_rows = _load_existing_rows(metrics_csv_path)
    cached_keys = {row_key(row) for row in existing_rows}

    simple_average_metric = SimpleAverageMetric()
    weighted_average_metric = WeightedAverageMetric()

    comparisons_found = 0
    metric_rows_created = 0
    metric_rows_reused = len(existing_rows)
    new_rows: list[dict[str, str]] = []

    print("Iniciando o cálculo da métrica global...")

    for key in sorted(available_keys):
        song_id, segment_id, transformation, comparison_type = key
        melody_scores = melody_groups[key]
        harmony_scores = harmony_groups[key]
        rhythm_scores = rhythm_groups[key]

        cache_key = _build_row_key(
            song_id=song_id,
            segment_id=segment_id,
            transformation=transformation,
            comparison_type=comparison_type,
            weights=validated_weights,
        )
        comparisons_found += 1
        if cache_key in cached_keys:
            continue

        simple_average = simple_average_metric.compute(
            melody_scores=melody_scores,
            harmony_scores=harmony_scores,
            rhythm_scores=rhythm_scores,
        )
        weighted_average = weighted_average_metric.compute(
            melody_scores=melody_scores,
            harmony_scores=harmony_scores,
            rhythm_scores=rhythm_scores,
            weights=validated_weights,
        )
        new_rows.append(
            {
                "song_id": song_id,
                "segment_id": segment_id,
                "transformation": transformation,
                "comparison_type": comparison_type,
                "simple_average": f"{simple_average:.6f}",
                "weighted_average": f"{weighted_average:.6f}",
                "weights_used": json.dumps(
                    validated_weights, ensure_ascii=False, sort_keys=True
                ),
                "score_global_final": f"{weighted_average:.6f}",
            }
        )
        cached_keys.add(cache_key)
        metric_rows_created += 1

    all_rows = existing_rows + new_rows
    all_rows.sort(
        key=lambda row: (
            row.get("song_id", ""),
            row.get("segment_id", ""),
            row.get("transformation", ""),
            row.get("comparison_type", ""),
            row.get("weights_used", ""),
        )
    )
    _write_metrics_csv(metrics_csv_path, all_rows)

    summary = GlobalMetricSummary(
        melody_metrics_path=melody_metrics_path,
        harmony_metrics_path=harmony_metrics_path,
        rhythm_metrics_path=rhythm_metrics_path,
        output_path=output_root,
        inspection_date=inspection_date,
        execution_time_seconds=time.perf_counter() - start_time,
        comparisons_found=comparisons_found,
        metric_rows_created=metric_rows_created,
        metric_rows_reused=metric_rows_reused,
    )
    _print_summary(summary, metrics_csv_path, validated_weights, missing_keys)
    return output_root


def _load_metric_rows(metrics_csv_path: Path) -> list[dict[str, str]]:
    """Carrega as linhas de um CSV de métricas."""

    with metrics_csv_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def _load_existing_rows(metrics_csv_path: Path) -> list[dict[str, str]]:
    """Carrega resultados previamente salvos."""

    if not metrics_csv_path.is_file():
        return []

    with metrics_csv_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def _group_rows_by_comparison(
    rows: list[dict[str, str]],
) -> dict[tuple[str, str, str, str], dict[str, float]]:
    """Agrupa as métricas por comparação."""

    grouped_rows: dict[tuple[str, str, str, str], dict[str, float]] = {}
    for row in rows:
        key = (
            row.get("song_id", ""),
            row.get("segment_id", ""),
            row.get("transformation", ""),
            row.get("comparison_type", "transformed"),
        )
        grouped_rows.setdefault(key, {})[row["metric"]] = float(row["value"])
    return grouped_rows


def _build_row_key(
    song_id: str,
    segment_id: str,
    transformation: str,
    comparison_type: str,
    weights: Mapping[str, float],
) -> tuple[str, str, str, str, str]:
    """Cria uma chave estável para reutilização de resultados."""

    return (
        song_id,
        segment_id,
        transformation,
        comparison_type,
        json.dumps(weights, ensure_ascii=False, sort_keys=True),
    )


def row_key(row: dict[str, str]) -> tuple[str, str, str, str, str]:
    """Extrai a chave estável de uma linha do CSV."""

    return _build_row_key(
        song_id=row.get("song_id", ""),
        segment_id=row.get("segment_id", ""),
        transformation=row.get("transformation", ""),
        comparison_type=row.get("comparison_type", "transformed"),
        weights=_load_json_field(row.get("weights_used", "{}")),
    )


def _load_json_field(value: Any) -> dict[str, Any]:
    """Converte um campo JSON textual em dicionário."""

    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip():
        loaded = json.loads(value)
        if isinstance(loaded, dict):
            return loaded
    return {}


def _write_metrics_csv(metrics_csv_path: Path, rows: list[dict[str, str]]) -> None:
    """Escreve o CSV consolidado da métrica global."""

    with metrics_csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "song_id",
                "segment_id",
                "transformation",
                "comparison_type",
                "simple_average",
                "weighted_average",
                "weights_used",
                "score_global_final",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def _print_summary(
    summary: GlobalMetricSummary,
    metrics_csv_path: Path,
    weights: Mapping[str, float],
    missing_keys: list[tuple[str, str, str, str]],
) -> None:
    """Exibe um resumo amigável da execução."""

    print("Cálculo da métrica global concluído.")
    print(f"Melodia: {summary.melody_metrics_path.as_posix()}")
    print(f"Harmonia: {summary.harmony_metrics_path.as_posix()}")
    print(f"Ritmo: {summary.rhythm_metrics_path.as_posix()}")
    print(f"Saída: {summary.output_path.as_posix()}")
    print(f"Comparações encontradas: {summary.comparisons_found}")
    print(f"Linhas criadas: {summary.metric_rows_created}")
    print(f"Linhas reutilizadas: {summary.metric_rows_reused}")
    print(
        "Pesos utilizados: "
        + json.dumps(weights, ensure_ascii=False, sort_keys=True)
    )
    if missing_keys:
        print(
            "Aviso: algumas comparações não possuíam resultados nas três modalidades "
            f"e foram ignoradas ({len(missing_keys)} combinações)."
        )
    print(f"Relatório CSV gerado em: {metrics_csv_path.as_posix()}")
    print(f"Data: {summary.inspection_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Tempo de execução: {summary.execution_time_seconds:.3f} segundos")
