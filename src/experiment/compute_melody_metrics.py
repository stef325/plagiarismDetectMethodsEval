"""Pipeline para cálculo das métricas de similaridade melódica."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import csv
import json
from pathlib import Path
import time
from typing import Any

from metrics.melody import (
    EditDistanceMetric,
    IntervalNGramSimilarityMetric,
    LongestCommonSubsequenceMetric,
)
from preprocessing.representation.melody_representation import MelodyRepresentation


@dataclass(frozen=True)
class MelodyMetricSummary:
    """Resumo da execução das métricas melódicas."""

    source_path: Path
    representations_path: Path
    output_path: Path
    inspection_date: datetime
    execution_time_seconds: float
    comparisons_found: int
    metric_rows_created: int
    metric_rows_reused: int


def compute_melody_metrics(
    transformations_path: str | Path,
    representations_path: str | Path,
    output_path: str | Path,
    interval_ngram_n: int = 2,
) -> Path:
    """Executa as métricas de similaridade sobre as transformações melódicas."""

    transformations_root = Path(transformations_path)
    representations_root = Path(representations_path)
    output_root = Path(output_path) / "melody"
    melody_transformations_root = transformations_root / "melody"
    inspection_date = datetime.now()
    start_time = time.perf_counter()

    if not melody_transformations_root.is_dir():
        raise FileNotFoundError(
            f"Diretório de transformações melódicas não encontrado: {melody_transformations_root}"
        )
    if not representations_root.is_dir():
        raise FileNotFoundError(
            f"Diretório de representações não encontrado: {representations_root}"
        )

    metadata_files = sorted(
        path
        for path in melody_transformations_root.rglob("metadata.csv")
        if "validation" not in path.parts
    )
    if not metadata_files:
        raise ValueError("Não há transformações melódicas para calcular métricas.")

    output_root.mkdir(parents=True, exist_ok=True)
    metrics_csv_path = output_root / "melody_similarity_metrics.csv"

    existing_rows = _load_existing_rows(metrics_csv_path)
    cached_keys = {row_key(row) for row in existing_rows}

    interval_metric = IntervalNGramSimilarityMetric()
    lcs_metric = LongestCommonSubsequenceMetric()
    edit_metric = EditDistanceMetric()

    comparisons_found = 0
    metric_rows_created = 0
    metric_rows_reused = len(existing_rows)
    new_rows: list[dict[str, str]] = []

    print("Iniciando o cálculo das métricas melódicas...")

    for metadata_path in metadata_files:
        metadata_rows = _load_metadata_rows(metadata_path)
        for row in metadata_rows:
            original = MelodyRepresentation.from_dict(
                _load_json(representations_root / row["source_file"])
            )
            transformed = MelodyRepresentation.from_dict(
                _load_json(metadata_path.parent / row["generated_file"])
            )

            comparison_pairs = [
                (
                    "transformed",
                    row.get("transformation", ""),
                    original,
                    transformed,
                ),
                (
                    "baseline_original",
                    "original_copy",
                    original,
                    MelodyRepresentation.from_dict(original.to_dict()),
                ),
            ]
            metric_specs = [
                ("interval_ngram_similarity", {"n": interval_ngram_n}),
                ("longest_common_subsequence", {}),
                ("edit_distance", {}),
            ]
            for comparison_type, transformation_label, source_representation, target_representation in comparison_pairs:
                comparisons_found += 1
                for metric_name, metric_parameters in metric_specs:
                    cache_key = _build_row_key(
                        song_id=row["song_id"],
                        segment_id=row["segment_id"],
                        transformation=transformation_label,
                        comparison_type=comparison_type,
                        metric=metric_name,
                        metric_parameters=metric_parameters,
                    )
                    if cache_key in cached_keys:
                        continue

                    value = _compute_metric(
                        metric_name=metric_name,
                        metric_parameters=metric_parameters,
                        original=source_representation,
                        transformed=target_representation,
                        interval_metric=interval_metric,
                        lcs_metric=lcs_metric,
                        edit_metric=edit_metric,
                    )
                    new_rows.append(
                        {
                            "song_id": row["song_id"],
                            "segment_id": row["segment_id"],
                            "transformation": transformation_label,
                            "comparison_type": comparison_type,
                            "metric": metric_name,
                            "metric_parameters": json.dumps(
                                metric_parameters, ensure_ascii=False, sort_keys=True
                            ),
                            "value": f"{value:.6f}",
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
            row.get("metric", ""),
            row.get("metric_parameters", ""),
        )
    )
    _write_metrics_csv(metrics_csv_path, all_rows)

    summary = MelodyMetricSummary(
        source_path=transformations_root,
        representations_path=representations_root,
        output_path=output_root,
        inspection_date=inspection_date,
        execution_time_seconds=time.perf_counter() - start_time,
        comparisons_found=comparisons_found,
        metric_rows_created=metric_rows_created,
        metric_rows_reused=metric_rows_reused,
    )
    _print_summary(summary, metrics_csv_path)
    return output_root


def _load_metadata_rows(metadata_path: Path) -> list[dict[str, str]]:
    """Carrega as linhas do CSV de metadados."""

    with metadata_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def _load_existing_rows(metrics_csv_path: Path) -> list[dict[str, str]]:
    """Carrega resultados previamente salvos."""

    if not metrics_csv_path.is_file():
        return []

    with metrics_csv_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def _load_json(path: Path) -> dict[str, Any]:
    """Carrega um arquivo JSON do disco."""

    return json.loads(path.read_text(encoding="utf-8"))


def _compute_metric(
    metric_name: str,
    metric_parameters: dict[str, Any],
    original: MelodyRepresentation,
    transformed: MelodyRepresentation,
    interval_metric: IntervalNGramSimilarityMetric,
    lcs_metric: LongestCommonSubsequenceMetric,
    edit_metric: EditDistanceMetric,
) -> float:
    """Executa a métrica solicitada."""

    if metric_name == "interval_ngram_similarity":
        return interval_metric.compute(original, transformed, **metric_parameters)
    if metric_name == "longest_common_subsequence":
        return lcs_metric.compute(original, transformed)
    if metric_name == "edit_distance":
        return edit_metric.compute(original, transformed)
    raise ValueError(f"Métrica melódica não suportada: {metric_name}")


def _build_row_key(
    song_id: str,
    segment_id: str,
    transformation: str,
    comparison_type: str,
    metric: str,
    metric_parameters: dict[str, Any],
) -> tuple[str, str, str, str, str, str]:
    """Cria uma chave estável para reutilização de resultados."""

    return (
        song_id,
        segment_id,
        transformation,
        comparison_type,
        metric,
        json.dumps(metric_parameters, ensure_ascii=False, sort_keys=True),
    )


def row_key(row: dict[str, str]) -> tuple[str, str, str, str, str, str]:
    """Extrai a chave estável de uma linha do CSV."""

    return _build_row_key(
        song_id=row.get("song_id", ""),
        segment_id=row.get("segment_id", ""),
        transformation=row.get("transformation", ""),
        comparison_type=row.get("comparison_type", "transformed"),
        metric=row.get("metric", ""),
        metric_parameters=_load_json_field(row.get("metric_parameters", "{}")),
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
    """Escreve o CSV consolidado das métricas."""

    with metrics_csv_path.open("w", encoding="utf-8", newline="") as file:
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


def _print_summary(summary: MelodyMetricSummary, metrics_csv_path: Path) -> None:
    """Exibe um resumo amigável da execução."""

    print("Cálculo das métricas melódicas concluído.")
    print(f"Origem: {summary.source_path.as_posix()}")
    print(f"Representações: {summary.representations_path.as_posix()}")
    print(f"Saída: {summary.output_path.as_posix()}")
    print(f"Comparações encontradas: {summary.comparisons_found}")
    print(f"Linhas criadas: {summary.metric_rows_created}")
    print(f"Linhas reutilizadas: {summary.metric_rows_reused}")
    print(f"Relatório CSV gerado em: {metrics_csv_path.as_posix()}")
    print(f"Data: {summary.inspection_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Tempo de execução: {summary.execution_time_seconds:.3f} segundos")
