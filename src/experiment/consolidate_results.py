"""Pipeline para consolidacao dos resultados do experimento."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import csv
import hashlib
import json
from pathlib import Path
import statistics
import time
from typing import Any


SIMILARITY_METRICS = {
    "melody": (
        "interval_ngram_similarity",
        "lcs_similarity",
        "edit_distance_similarity",
    ),
    "harmony": (
        "chord_ngram_similarity",
        "harmonic_edit_distance",
        "pitch_class_similarity",
    ),
    "rhythm": (
        "rhythm_ngram_similarity",
        "ioi_similarity",
        "rhythmic_edit_distance",
    ),
}


@dataclass(frozen=True)
class ConsolidationSummary:
    """Resumo consolidado do experimento."""

    similarity_path: Path
    robustness_path: Path
    interpretability_path: Path
    output_path: Path
    inspection_date: datetime
    execution_time_seconds: float
    total_pairs: int
    experiment_count: int
    fingerprint: str


def consolidate_results(
    similarity_results_path: str | Path | None = None,
    robustness_results_path: str | Path | None = None,
    interpretability_results_path: str | Path | None = None,
    output_path: str | Path = "data/results/consolidated",
) -> Path:
    """Consolida os resultados produzidos pelo experimento."""

    similarity_path = _resolve_similarity_results_path(similarity_results_path)
    robustness_path = _resolve_robustness_results_path(robustness_results_path)
    interpretability_path = _resolve_interpretability_results_path(
        interpretability_results_path
    )
    output_root = Path(output_path)
    inspection_date = datetime.now()
    start_time = time.perf_counter()

    for path, label in (
        (similarity_path, "similaridade"),
        (robustness_path, "robustez"),
        (interpretability_path, "interpretabilidade"),
    ):
        if not path.is_file():
            raise FileNotFoundError(f"Arquivo de {label} nao encontrado: {path}")

    output_root.mkdir(parents=True, exist_ok=True)
    similarity_csv = output_root / "consolidated_similarity.csv"
    robustness_csv = output_root / "consolidated_robustness.csv"
    interpretability_csv = output_root / "consolidated_interpretability.csv"
    experiment_summary_csv = output_root / "experiment_summary.csv"
    statistics_summary_csv = output_root / "statistics_summary.csv"
    json_path = output_root / "consolidated_results.json"
    report_path = output_root / "consolidated_results.md"
    cache_path = output_root / "consolidated_results_cache.json"

    fingerprint = _compute_fingerprint(
        similarity_path=similarity_path,
        robustness_path=robustness_path,
        interpretability_path=interpretability_path,
    )
    if _is_cache_valid(
        cache_path,
        similarity_csv,
        robustness_csv,
        interpretability_csv,
        experiment_summary_csv,
        statistics_summary_csv,
        json_path,
        report_path,
        fingerprint,
    ):
        _print_cache_summary(cache_path, output_root)
        return output_root

    similarity_rows = _load_csv(similarity_path)
    robustness_rows = _load_csv(robustness_path)
    interpretability_rows = _load_csv(interpretability_path)

    similarity_consolidated = _build_similarity_consolidation(similarity_rows)
    robustness_consolidated = _build_robustness_consolidation(robustness_rows)
    interpretability_consolidated = _build_interpretability_consolidation(
        interpretability_rows
    )
    experiment_summary_rows = _build_experiment_summary(
        similarity_consolidated,
        robustness_consolidated,
        interpretability_consolidated,
    )
    statistics_summary_rows = _build_statistics_summary(similarity_rows)

    _write_csv(similarity_csv, similarity_consolidated)
    _write_csv(robustness_csv, robustness_consolidated)
    _write_csv(interpretability_csv, interpretability_consolidated)
    _write_csv(experiment_summary_csv, experiment_summary_rows)
    _write_csv(statistics_summary_csv, statistics_summary_rows)

    payload = {
        "similarity_results_path": similarity_path.as_posix(),
        "robustness_results_path": robustness_path.as_posix(),
        "interpretability_results_path": interpretability_path.as_posix(),
        "generated_at": inspection_date.isoformat(),
        "fingerprint": fingerprint,
        "summary": {
            "total_pairs": len(similarity_consolidated),
            "experiment_count": len(experiment_summary_rows),
            "execution_time_seconds": time.perf_counter() - start_time,
        },
        "consolidated_similarity": similarity_consolidated,
        "consolidated_robustness": robustness_consolidated,
        "consolidated_interpretability": interpretability_consolidated,
        "experiment_summary": experiment_summary_rows,
        "statistics_summary": statistics_summary_rows,
    }
    _write_json(json_path, payload)

    summary = ConsolidationSummary(
        similarity_path=similarity_path,
        robustness_path=robustness_path,
        interpretability_path=interpretability_path,
        output_path=output_root,
        inspection_date=inspection_date,
        execution_time_seconds=time.perf_counter() - start_time,
        total_pairs=len(similarity_consolidated),
        experiment_count=len(experiment_summary_rows),
        fingerprint=fingerprint,
    )
    _write_report(
        report_path,
        summary,
        similarity_consolidated,
        robustness_consolidated,
        interpretability_consolidated,
        experiment_summary_rows,
        statistics_summary_rows,
    )
    _write_cache(
        cache_path,
        fingerprint,
        similarity_csv,
        robustness_csv,
        interpretability_csv,
        experiment_summary_csv,
        statistics_summary_csv,
        json_path,
        report_path,
        summary.total_pairs,
        summary.experiment_count,
    )
    _print_summary(summary, report_path)
    return output_root


def _resolve_similarity_results_path(path_value: str | Path | None) -> Path:
    """Resolve o arquivo consolidado de similaridade."""

    candidates = [
        Path("data/results/experiment/similarity_results.csv"),
        Path("data/results/similarity_results.csv"),
    ]
    return _resolve_path(path_value, candidates)


def _resolve_robustness_results_path(path_value: str | Path | None) -> Path:
    """Resolve o arquivo consolidado de robustez."""

    candidates = [
        Path("data/results/evaluation/robustness_metrics.csv"),
    ]
    return _resolve_path(path_value, candidates)


def _resolve_interpretability_results_path(path_value: str | Path | None) -> Path:
    """Resolve o arquivo consolidado de interpretabilidade."""

    candidates = [
        Path("data/results/evaluation/interpretability/interpretability_results.csv"),
    ]
    return _resolve_path(path_value, candidates)


def _resolve_path(path_value: str | Path | None, defaults: list[Path]) -> Path:
    """Resolve um caminho com candidatos padrao."""

    if path_value is not None:
        path = Path(path_value)
        if path.is_file():
            return path
        if path.is_dir():
            for candidate in defaults:
                nested = path / candidate.name
                if nested.is_file():
                    return nested
        if path.suffix:
            return path
    for candidate in defaults:
        if candidate.is_file():
            return candidate
    return defaults[0]


def _load_csv(path: Path) -> list[dict[str, str]]:
    """Carrega um CSV."""

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _build_similarity_consolidation(
    rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Monta a tabela consolidada de similaridade."""

    consolidated: list[dict[str, str]] = []
    for row in rows:
        if row.get("record_type") == "metric_summary":
            continue
        melody_score = _mean(
            [
                float(row[column])
                for column in SIMILARITY_METRICS["melody"]
                if row.get(column)
            ]
        )
        harmony_score = _mean(
            [
                float(row[column])
                for column in SIMILARITY_METRICS["harmony"]
                if row.get(column)
            ]
        )
        rhythm_score = _mean(
            [
                float(row[column])
                for column in SIMILARITY_METRICS["rhythm"]
                if row.get(column)
            ]
        )
        consolidated.append(
            {
                "pair_id": row.get("pair_id", ""),
                "pair_type": row.get("pair_type", ""),
                "transformation": row.get("transformation", ""),
                "interval_ngram_similarity": row.get("interval_ngram_similarity", ""),
                "lcs_similarity": row.get("lcs_similarity", ""),
                "edit_distance_similarity": row.get("edit_distance_similarity", ""),
                "chord_ngram_similarity": row.get("chord_ngram_similarity", ""),
                "harmonic_edit_distance": row.get("harmonic_edit_distance", ""),
                "pitch_class_similarity": row.get("pitch_class_similarity", ""),
                "rhythm_ngram_similarity": row.get("rhythm_ngram_similarity", ""),
                "ioi_similarity": row.get("ioi_similarity", ""),
                "rhythmic_edit_distance": row.get("rhythmic_edit_distance", ""),
                "score_melody": f"{melody_score:.6f}",
                "score_harmony": f"{harmony_score:.6f}",
                "score_rhythm": f"{rhythm_score:.6f}",
                "score_global": row.get("weighted_average", ""),
                "simple_average": row.get("simple_average", ""),
                "weighted_average": row.get("weighted_average", ""),
                "comparison_representation": row.get("comparison_representation", ""),
                "experiment_category": _infer_experiment_category(row),
            }
        )
    return consolidated


def _build_robustness_consolidation(
    rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Monta a tabela consolidada de robustez."""

    consolidated: list[dict[str, str]] = []
    for row in rows:
        if row.get("record_type") != "metric_summary":
            continue
        consolidated.append(
            {
                "metric": row.get("metric_name", ""),
                "precision": row.get("precision", ""),
                "recall": row.get("recall", ""),
                "f1_score": row.get("f1_score", ""),
                "false_negative_rate": row.get("false_negative_rate", ""),
            }
        )
    return consolidated


def _build_interpretability_consolidation(
    rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Monta a tabela consolidada de interpretabilidade."""

    return [
        {
            "transformation": row.get("transformation", ""),
            "component_transformed": row.get("component_transformed", ""),
            "score_melody": row.get("score_melody", ""),
            "score_harmony": row.get("score_harmony", ""),
            "score_rhythm": row.get("score_rhythm", ""),
            "score_global": row.get("score_global", ""),
            "observations": row.get("observations", ""),
        }
        for row in rows
    ]


def _build_experiment_summary(
    similarity_rows: list[dict[str, str]],
    robustness_rows: list[dict[str, str]],
    interpretability_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Monta o resumo por experimento."""

    similarity_groups = _group_by_experiment(similarity_rows)
    interpretability_groups = _group_by_experiment(interpretability_rows)
    robustness_summary = _aggregate_robustness(robustness_rows)

    experiment_rows: list[dict[str, str]] = []
    for category, rows in sorted(similarity_groups.items()):
        if category == "Outros":
            continue
        melody_scores = [float(row["score_melody"]) for row in rows if row["score_melody"]]
        harmony_scores = [float(row["score_harmony"]) for row in rows if row["score_harmony"]]
        rhythm_scores = [float(row["score_rhythm"]) for row in rows if row["score_rhythm"]]
        global_scores = [float(row["score_global"]) for row in rows if row["score_global"]]
        interpretability_group = interpretability_groups.get(category, [])
        experiment_rows.append(
            {
                "experiment": category,
                "pair_count": str(len(rows)),
                "mean_melody_score": f"{_mean(melody_scores):.6f}",
                "mean_harmony_score": f"{_mean(harmony_scores):.6f}",
                "mean_rhythm_score": f"{_mean(rhythm_scores):.6f}",
                "mean_global_score": f"{_mean(global_scores):.6f}",
                "precision": f"{robustness_summary.get('precision', 0.0):.6f}",
                "recall": f"{robustness_summary.get('recall', 0.0):.6f}",
                "f1_score": f"{robustness_summary.get('f1_score', 0.0):.6f}",
                "false_negative_rate": f"{robustness_summary.get('false_negative_rate', 0.0):.6f}",
                "interpretability_pairs": str(len(interpretability_group)),
                "interpretability_mean_global": f"{_mean([float(row['score_global']) for row in interpretability_group]):.6f}",
            }
        )
    return experiment_rows


def _build_statistics_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Calcula estatisticas gerais por familia de metricas."""

    summary_rows: list[dict[str, str]] = []
    for family_name, columns in SIMILARITY_METRICS.items():
        values = [
            float(row[column])
            for row in rows
            for column in columns
            if row.get(column)
        ]
        summary_rows.append(
            {
                "metric_family": family_name,
                "mean": f"{_mean(values):.6f}",
                "median": f"{_median(values):.6f}",
                "std": f"{_std(values):.6f}",
                "minimum": f"{min(values):.6f}" if values else "0.000000",
                "q1": f"{_quantile(values, 0.25):.6f}",
                "q3": f"{_quantile(values, 0.75):.6f}",
                "maximum": f"{max(values):.6f}" if values else "0.000000",
            }
        )

    global_values = [
        float(row["weighted_average"])
        for row in rows
        if row.get("weighted_average")
    ]
    summary_rows.append(
        {
            "metric_family": "global",
            "mean": f"{_mean(global_values):.6f}",
            "median": f"{_median(global_values):.6f}",
            "std": f"{_std(global_values):.6f}",
            "minimum": f"{min(global_values):.6f}" if global_values else "0.000000",
            "q1": f"{_quantile(global_values, 0.25):.6f}",
            "q3": f"{_quantile(global_values, 0.75):.6f}",
            "maximum": f"{max(global_values):.6f}" if global_values else "0.000000",
        }
    )
    return summary_rows


def _group_by_transformation(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    """Agrupa linhas pelo experimento/transformacao."""

    groups: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        transformation = row.get("transformation", "") or row.get("experiment", "")
        if not transformation:
            transformation = row.get("component_transformed", "")
        if not transformation:
            continue
        groups.setdefault(transformation, []).append(row)
    return groups


def _group_by_experiment(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    """Agrupa linhas pela categoria experimental."""

    groups: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        category = _infer_experiment_category(row)
        groups.setdefault(category, []).append(row)
    return groups


def _infer_experiment_category(row: dict[str, str]) -> str:
    """Infere a categoria do experimento a partir da representacao comparada."""

    representation = row.get("comparison_representation", "")
    if "/transformations/melody/" in representation:
        return "Transformações Melódicas"
    if "/transformations/harmony/" in representation:
        return "Transformações Harmônicas"
    if "/transformations/rhythm/" in representation:
        return "Transformações Rítmicas"
    if "/transformations/combined/" in representation:
        return "Transformações Combinadas"
    transformation = row.get("transformation", "")
    if transformation in {"transpose", "interval_modification", "ornamentation", "simplification"}:
        return "Transformações Melódicas"
    if transformation in {"chord_substitution", "reharmonization"}:
        return "Transformações Harmônicas"
    if transformation in {"tempo_change", "duration_scaling", "partial_rhythm_modification"}:
        return "Transformações Rítmicas"
    if transformation in {
        "melody_harmony",
        "melody_rhythm",
        "harmony_rhythm",
        "melody_harmony_rhythm",
    }:
        return "Transformações Combinadas"
    return "Outros"


def _aggregate_robustness(rows: list[dict[str, str]]) -> dict[str, float]:
    """Agrega as estatisticas de robustez."""

    precision_values = [float(row["precision"]) for row in rows if row.get("metric_name")]
    recall_values = [float(row["recall"]) for row in rows if row.get("metric_name")]
    f1_values = [float(row["f1_score"]) for row in rows if row.get("metric_name")]
    fnr_values = [float(row["false_negative_rate"]) for row in rows if row.get("metric_name")]
    return {
        "precision": _mean(precision_values),
        "recall": _mean(recall_values),
        "f1_score": _mean(f1_values),
        "false_negative_rate": _mean(fnr_values),
    }


def _mean(values: list[float]) -> float:
    """Calcula a media."""

    if not values:
        return 0.0
    return statistics.fmean(values)


def _median(values: list[float]) -> float:
    """Calcula a mediana."""

    if not values:
        return 0.0
    return statistics.median(values)


def _std(values: list[float]) -> float:
    """Calcula o desvio padrao."""

    if len(values) <= 1:
        return 0.0
    return statistics.pstdev(values)


def _quantile(values: list[float], percentile: float) -> float:
    """Calcula um quartil simples."""

    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * percentile
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    if lower == upper:
        return ordered[lower]
    fraction = index - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    """Escreve um CSV."""

    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    """Escreve um JSON."""

    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _write_report(
    report_path: Path,
    summary: ConsolidationSummary,
    similarity_rows: list[dict[str, str]],
    robustness_rows: list[dict[str, str]],
    interpretability_rows: list[dict[str, str]],
    experiment_summary_rows: list[dict[str, str]],
    statistics_summary_rows: list[dict[str, str]],
) -> None:
    """Escreve o relatorio Markdown da consolidacao."""

    lines = [
        "# Relatório de Consolidação dos Resultados",
        "",
        f"Data: {summary.inspection_date.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Resumo do experimento",
        "",
        f"- Quantidade total de pares: {summary.total_pairs}",
        f"- Quantidade de experimentos executados: {summary.experiment_count}",
        f"- Tempo de execução: {summary.execution_time_seconds:.3f} segundos",
        "",
        "## Tabela de Similaridade",
        "",
        "| pair_id | pair_type | transformação | score melódico | score harmônico | score rítmico | score global |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in similarity_rows[:20]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row.get("pair_id", ""),
                    row.get("pair_type", ""),
                    row.get("transformation", ""),
                    row.get("score_melody", ""),
                    row.get("score_harmony", ""),
                    row.get("score_rhythm", ""),
                    row.get("score_global", ""),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Tabela de Robustez",
            "",
            "| métrica | Precision | Recall | F1-score | False Negative Rate |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in robustness_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row.get("metric", ""),
                    row.get("precision", ""),
                    row.get("recall", ""),
                    row.get("f1_score", ""),
                    row.get("false_negative_rate", ""),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Tabela de Interpretabilidade",
            "",
            "| transformação | componente alterado | score melódico | score harmônico | score rítmico | score global | observações |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in interpretability_rows[:20]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row.get("transformation", ""),
                    row.get("component_transformed", ""),
                    row.get("score_melody", ""),
                    row.get("score_harmony", ""),
                    row.get("score_rhythm", ""),
                    row.get("score_global", ""),
                    row.get("observations", ""),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Resumo por experimento",
            "",
            "| experimento | quantidade de pares | média melódica | média harmônica | média rítmica | média global |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in experiment_summary_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row.get("experiment", ""),
                    row.get("pair_count", ""),
                    row.get("mean_melody_score", ""),
                    row.get("mean_harmony_score", ""),
                    row.get("mean_rhythm_score", ""),
                    row.get("mean_global_score", ""),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Estatísticas gerais",
            "",
            "| família | média | mediana | desvio padrão | mínimo | Q1 | Q3 | máximo |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in statistics_summary_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row.get("metric_family", ""),
                    row.get("mean", ""),
                    row.get("median", ""),
                    row.get("std", ""),
                    row.get("minimum", ""),
                    row.get("q1", ""),
                    row.get("q3", ""),
                    row.get("maximum", ""),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Principais resultados",
            "",
            "- Os resultados consolidados foram agrupados por tipo de transformação.",
            "- A interpretação considera as saídas já produzidas pelos pipelines anteriores.",
            "- As estatísticas gerais usam apenas os resultados existentes.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_cache(
    cache_path: Path,
    fingerprint: str,
    similarity_csv: Path,
    robustness_csv: Path,
    interpretability_csv: Path,
    experiment_summary_csv: Path,
    statistics_summary_csv: Path,
    json_path: Path,
    report_path: Path,
    total_pairs: int,
    experiment_count: int,
) -> None:
    """Escreve o cache de reutilizacao."""

    cache_path.write_text(
        json.dumps(
            {
                "fingerprint": fingerprint,
                "similarity_csv": similarity_csv.as_posix(),
                "robustness_csv": robustness_csv.as_posix(),
                "interpretability_csv": interpretability_csv.as_posix(),
                "experiment_summary_csv": experiment_summary_csv.as_posix(),
                "statistics_summary_csv": statistics_summary_csv.as_posix(),
                "json_path": json_path.as_posix(),
                "report_path": report_path.as_posix(),
                "total_pairs": total_pairs,
                "experiment_count": experiment_count,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def _is_cache_valid(
    cache_path: Path,
    similarity_csv: Path,
    robustness_csv: Path,
    interpretability_csv: Path,
    experiment_summary_csv: Path,
    statistics_summary_csv: Path,
    json_path: Path,
    report_path: Path,
    fingerprint: str,
) -> bool:
    """Verifica se o cache ainda é valido."""

    if not all(
        path.is_file()
        for path in (
            cache_path,
            similarity_csv,
            robustness_csv,
            interpretability_csv,
            experiment_summary_csv,
            statistics_summary_csv,
            json_path,
            report_path,
        )
    ):
        return False
    cached_payload = json.loads(cache_path.read_text(encoding="utf-8"))
    return cached_payload.get("fingerprint") == fingerprint


def _print_cache_summary(cache_path: Path, output_root: Path) -> None:
    """Exibe um resumo quando a consolidacao e reutilizada."""

    cached_payload = json.loads(cache_path.read_text(encoding="utf-8"))
    print("Resultados consolidados reutilizados a partir do cache.")
    print(f"Saída: {output_root.as_posix()}")
    print(f"Total de pares: {cached_payload.get('total_pairs', 0)}")
    print(f"Quantidade de experimentos: {cached_payload.get('experiment_count', 0)}")


def _print_summary(summary: ConsolidationSummary, report_path: Path) -> None:
    """Exibe um resumo amigavel da consolidacao."""

    print("Consolidação dos resultados concluída.")
    print(f"Quantidade total de pares: {summary.total_pairs}")
    print(f"Quantidade de experimentos executados: {summary.experiment_count}")
    print(f"Tempo de execução: {summary.execution_time_seconds:.3f} segundos")
    print(f"Relatório gerado em: {report_path.as_posix()}")


def _compute_fingerprint(
    similarity_path: Path,
    robustness_path: Path,
    interpretability_path: Path,
) -> str:
    """Gera uma assinatura estavel dos resultados utilizados."""

    digest = hashlib.sha256()
    for path in (similarity_path, robustness_path, interpretability_path):
        digest.update(path.as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    digest.update(Path(__file__).read_bytes())
    return digest.hexdigest()
