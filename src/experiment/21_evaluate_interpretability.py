"""Pipeline para avaliacao da interpretabilidade das metricas de similaridade."""

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


FAMILY_COLUMNS = {
    "Melodia": (
        "interval_ngram_similarity",
        "lcs_similarity",
        "edit_distance_similarity",
    ),
    "Harmonia": (
        "chord_ngram_similarity",
        "harmonic_edit_distance",
        "pitch_class_similarity",
    ),
    "Ritmo": (
        "rhythm_ngram_similarity",
        "ioi_similarity",
        "rhythmic_edit_distance",
    ),
}


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
class TransformationMetadataRecord:
    """Representa os metadados de uma transformação aplicada."""

    generated_path: Path
    component_category: str
    transformation_name: str
    transformed_components: tuple[str, ...]
    parameters: dict[str, Any]
    combination_name: str | None = None


@dataclass(frozen=True)
class PairInterpretabilityRecord:
    """Resultado interpretativo associado a um par experimental."""

    pair_id: str
    pair_type: str
    transformation: str
    component_transformed: str
    score_melody: float
    score_harmony: float
    score_rhythm: float
    simple_average: float
    weighted_average: float
    score_global: float
    score_gap: float
    transformed_component_score: float
    global_delta: float
    observations: str


@dataclass(frozen=True)
class CategoryInterpretabilityStats:
    """Estatísticas resumidas por tipo de transformação."""

    category: str
    pair_count: int
    target_mean: float
    target_median: float
    target_std: float
    target_min: float
    target_max: float
    global_mean: float
    global_median: float
    global_std: float
    global_min: float
    global_max: float
    gap_mean: float
    gap_median: float
    gap_std: float
    gap_min: float
    gap_max: float


@dataclass(frozen=True)
class CategoryEvidence:
    """Evidências interpretativas agregadas por categoria."""

    category: str
    most_sensitive_family: str
    most_stable_family: str
    most_variable_family: str
    global_behavior: str
    family_similarity_means: dict[str, float]
    simple_average_mean: float
    weighted_average_mean: float


@dataclass(frozen=True)
class InterpretabilitySummary:
    """Resumo consolidado da avaliacao de interpretabilidade."""

    pairs_path: Path
    similarity_results_path: Path
    transformations_root: Path
    output_path: Path
    inspection_date: datetime
    execution_time_seconds: float
    total_pairs: int
    positive_pairs: int
    negative_pairs: int
    transformation_categories: int
    fingerprint: str


def evaluate_interpretability(
    experiment_pairs_path: str | Path | None = None,
    similarity_results_path: str | Path | None = None,
    transformations_root: str | Path | None = None,
    output_path: str | Path = "data/results/evaluation/interpretability",
) -> Path:
    """Avalia se as metricas refletem o componente musical transformado."""

    pairs_path = _resolve_experiment_pairs_path(experiment_pairs_path)
    results_path = _resolve_similarity_results_path(similarity_results_path)
    transformations_root_path = _resolve_transformations_root(transformations_root)
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
    if not transformations_root_path.is_dir():
        raise FileNotFoundError(
            f"Diretorio de transformacoes nao encontrado: {transformations_root_path}"
        )

    output_root.mkdir(parents=True, exist_ok=True)
    csv_path = output_root / "interpretability_results.csv"
    json_path = output_root / "interpretability_results.json"
    report_path = output_root / "interpretability_report.md"
    cache_path = output_root / "interpretability_cache.json"

    fingerprint = _compute_fingerprint(
        pairs_path=pairs_path,
        results_path=results_path,
        transformations_root=transformations_root_path,
    )
    if _is_cache_valid(cache_path, csv_path, json_path, report_path, fingerprint):
        _print_cache_summary(cache_path, csv_path, json_path, report_path)
        return output_root

    print("Iniciando a avaliacao de interpretabilidade das metricas...")

    pair_records = _load_pairs(pairs_path)
    similarity_rows = _load_similarity_rows(results_path)
    rows_by_pair_id = {row["pair_id"]: row for row in similarity_rows}
    metadata_map = _load_transformation_metadata(transformations_root_path)

    missing_pair_ids = sorted(
        pair.pair_id for pair in pair_records if pair.pair_id not in rows_by_pair_id
    )
    if missing_pair_ids:
        raise ValueError(
            "Alguns pares experimentais nao possuem resultados de similaridade: "
            + ", ".join(missing_pair_ids[:10])
        )

    interpretability_rows: list[PairInterpretabilityRecord] = []
    category_groups: dict[str, list[PairInterpretabilityRecord]] = {}

    for pair in pair_records:
        similarity_row = rows_by_pair_id[pair.pair_id]
        family_scores = _compute_family_scores(similarity_row)
        weighted_average = float(similarity_row["weighted_average"])
        simple_average = float(similarity_row["simple_average"])
        metadata = _resolve_metadata_for_pair(pair, metadata_map)
        component_category = (
            metadata.component_category if metadata is not None else "Não aplicável"
        )
        transformation_name = _resolve_transformation_name(pair, metadata)
        transformed_component_score = _compute_transformed_component_score(
            component_category, family_scores
        )
        score_gap = max(
            family_scores["Melodia"],
            family_scores["Harmonia"],
            family_scores["Ritmo"],
        ) - min(
            family_scores["Melodia"],
            family_scores["Harmonia"],
            family_scores["Ritmo"],
        )
        global_delta = weighted_average - transformed_component_score
        observations = _build_pair_observation(
            pair_type=pair.pair_type,
            component_category=component_category,
            metadata=metadata,
            family_scores=family_scores,
            weighted_average=weighted_average,
            transformed_component_score=transformed_component_score,
        )
        record = PairInterpretabilityRecord(
            pair_id=pair.pair_id,
            pair_type=pair.pair_type,
            transformation=transformation_name,
            component_transformed=component_category,
            score_melody=family_scores["Melodia"],
            score_harmony=family_scores["Harmonia"],
            score_rhythm=family_scores["Ritmo"],
            simple_average=simple_average,
            weighted_average=weighted_average,
            score_global=weighted_average,
            score_gap=score_gap,
            transformed_component_score=transformed_component_score,
            global_delta=global_delta,
            observations=observations,
        )
        interpretability_rows.append(record)
        if pair.pair_type == "positive" and component_category != "Não aplicável":
            category_groups.setdefault(component_category, []).append(record)

    category_stats = [
        _build_category_stats(category, records)
        for category, records in sorted(category_groups.items())
    ]
    category_evidence = [
        _build_category_evidence(category, records)
        for category, records in sorted(category_groups.items())
    ]

    _write_csv(csv_path, interpretability_rows)
    _write_json(
        json_path,
        {
            "pairs_path": pairs_path.as_posix(),
            "similarity_results_path": results_path.as_posix(),
            "transformations_root": transformations_root_path.as_posix(),
            "generated_at": inspection_date.isoformat(),
            "fingerprint": fingerprint,
            "summary": {
                "total_pairs": len(pair_records),
                "positive_pairs": sum(
                    1 for pair in pair_records if pair.pair_type == "positive"
                ),
                "negative_pairs": sum(
                    1 for pair in pair_records if pair.pair_type == "negative"
                ),
                "transformation_categories": len(category_stats),
                "execution_time_seconds": time.perf_counter() - start_time,
            },
            "category_stats": [stats.__dict__ for stats in category_stats],
            "category_evidence": [evidence.__dict__ for evidence in category_evidence],
            "results": [record.__dict__ for record in interpretability_rows],
        },
    )
    summary = InterpretabilitySummary(
        pairs_path=pairs_path,
        similarity_results_path=results_path,
        transformations_root=transformations_root_path,
        output_path=output_root,
        inspection_date=inspection_date,
        execution_time_seconds=time.perf_counter() - start_time,
        total_pairs=len(pair_records),
        positive_pairs=sum(1 for pair in pair_records if pair.pair_type == "positive"),
        negative_pairs=sum(1 for pair in pair_records if pair.pair_type == "negative"),
        transformation_categories=len(category_stats),
        fingerprint=fingerprint,
    )
    _write_report(report_path, summary, category_stats, category_evidence)
    _write_cache(
        cache_path=cache_path,
        fingerprint=fingerprint,
        csv_path=csv_path,
        json_path=json_path,
        report_path=report_path,
        total_pairs=summary.total_pairs,
        positive_pairs=summary.positive_pairs,
        negative_pairs=summary.negative_pairs,
    )
    _print_summary(summary, report_path, category_stats, category_evidence)
    return output_root


def _resolve_experiment_pairs_path(experiment_pairs_path: str | Path | None) -> Path:
    """Resolve o caminho do arquivo de pares experimentais."""

    candidates = _candidate_experiment_pairs_paths(experiment_pairs_path)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return candidates[0]


def _candidate_experiment_pairs_paths(
    experiment_pairs_path: str | Path | None,
) -> list[Path]:
    """Gera candidatos para localizar os pares experimentais."""

    default_candidates = [
        Path("data/results/experiment/pairs/experiment_pairs.json"),
        Path("data/results/experiment/experiment_pairs.json"),
        Path("data/experiment/experiment_pairs.json"),
    ]
    if experiment_pairs_path is None:
        return default_candidates

    path = Path(experiment_pairs_path)
    if path.is_file():
        return [
            path,
            path.parent / "experiment_pairs.json",
            path.parent / "pairs" / "experiment_pairs.json",
            *default_candidates,
        ]
    if path.is_dir():
        return [
            path / "experiment_pairs.json",
            path / "pairs" / "experiment_pairs.json",
            path.parent / "experiment_pairs.json",
            path.parent / "pairs" / "experiment_pairs.json",
            *default_candidates,
        ]
    if path.suffix.lower() == ".json":
        return [
            path,
            path.parent / "experiment_pairs.json",
            path.parent / "pairs" / "experiment_pairs.json",
            *default_candidates,
        ]
    return [path / "experiment_pairs.json", *default_candidates]


def _resolve_similarity_results_path(
    similarity_results_path: str | Path | None,
) -> Path:
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

    default_candidates = [
        Path("data/results/experiment/similarity_results.csv"),
        Path("data/results/similarity_results.csv"),
    ]
    if similarity_results_path is None:
        return default_candidates

    path = Path(similarity_results_path)
    if path.is_file():
        return [path, path.parent / "similarity_results.csv", *default_candidates]
    if path.is_dir():
        return [
            path / "similarity_results.csv",
            path.parent / "similarity_results.csv",
            *default_candidates,
        ]
    if path.suffix.lower() == ".csv":
        return [path, path.parent / "similarity_results.csv", *default_candidates]
    return [path / "similarity_results.csv", *default_candidates]


def _resolve_transformations_root(transformations_root: str | Path | None) -> Path:
    """Resolve o diretorio das transformacoes."""

    if transformations_root is None:
        return Path("data/processed/transformations")
    return Path(transformations_root)


def _load_pairs(pairs_path: Path) -> list[ExperimentPairRecord]:
    """Carrega os pares experimentais do JSON."""

    payload = json.loads(pairs_path.read_text(encoding="utf-8"))
    pairs: list[ExperimentPairRecord] = []
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


def _read_csv(path: Path) -> list[dict[str, str]]:
    """Lê um CSV para lista de dicionários."""

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _load_transformation_metadata(
    transformations_root: Path,
) -> dict[str, TransformationMetadataRecord]:
    """Carrega os metadados das transformacoes."""

    metadata_map: dict[str, TransformationMetadataRecord] = {}
    for metadata_path in sorted(
        path
        for path in transformations_root.rglob("metadata.csv")
        if "validation" not in path.parts and "experiment" not in path.parts
    ):
        category = _infer_category_from_metadata_path(transformations_root, metadata_path)
        rows = _read_csv(metadata_path)
        for row in rows:
            generated_path = (metadata_path.parent / row["generated_file"]).resolve()
            transformation_name, transformed_components, parameters, combination_name = (
                _parse_metadata_row(category, row)
            )
            metadata_map[str(generated_path)] = TransformationMetadataRecord(
                generated_path=generated_path,
                component_category=category,
                transformation_name=transformation_name,
                transformed_components=transformed_components,
                parameters=parameters,
                combination_name=combination_name,
            )
    return metadata_map


def _infer_category_from_metadata_path(
    transformations_root: Path,
    metadata_path: Path,
) -> str:
    """Infere a categoria a partir do caminho do metadado."""

    relative_parts = metadata_path.relative_to(transformations_root).parts
    if not relative_parts:
        return "Não aplicável"
    category = relative_parts[0]
    if category == "melody":
        return "Melodia"
    if category == "harmony":
        return "Harmonia"
    if category == "rhythm":
        return "Ritmo"
    if category == "combined":
        return "Combinações"
    return "Não aplicável"


def _parse_metadata_row(
    category: str,
    row: dict[str, str],
) -> tuple[str, tuple[str, ...], dict[str, Any], str | None]:
    """Normaliza uma linha de metadados em informacoes interpretaveis."""

    parameters = _load_json_field(row.get("parameters", "{}"))
    if category == "Combinações":
        combination_name = row.get("combination", "")
        individual_transformations = _load_json_field(
            row.get("individual_transformations", "{}")
        )
        transformed_components = tuple(
            {
                "melody": "Melodia",
                "harmony": "Harmonia",
                "rhythm": "Ritmo",
            }[key]
            for key in sorted(individual_transformations)
            if key in {"melody", "harmony", "rhythm"}
        )
        return (
            combination_name or "combination",
            transformed_components or ("Melodia", "Harmonia", "Ritmo"),
            parameters,
            combination_name or None,
        )

    transformation_name = row.get("transformation", "") or "unknown"
    return (
        transformation_name,
        (category,),
        parameters,
        None,
    )


def _resolve_metadata_for_pair(
    pair: ExperimentPairRecord,
    metadata_map: dict[str, TransformationMetadataRecord],
) -> TransformationMetadataRecord | None:
    """Localiza o metadado associado a uma representacao transformada."""

    candidate_paths = [
        _resolve_path(pair.comparison_representation).resolve(),
        (_resolve_path(pair.comparison_representation).resolve()),
    ]
    for candidate in candidate_paths:
        metadata = metadata_map.get(str(candidate))
        if metadata is not None:
            return metadata
    return None


def _resolve_transformation_name(
    pair: ExperimentPairRecord,
    metadata: TransformationMetadataRecord | None,
) -> str:
    """Obtém o nome textual da transformação."""

    if metadata is not None:
        if metadata.combination_name is not None:
            return metadata.combination_name
        return metadata.transformation_name
    if pair.transformation:
        return pair.transformation
    return "unknown"


def _compute_family_scores(similarity_row: dict[str, str]) -> dict[str, float]:
    """Calcula um score agregado por familia de metricas."""

    family_scores: dict[str, float] = {}
    for family_name, columns in FAMILY_COLUMNS.items():
        values = [float(similarity_row[column]) for column in columns if column in similarity_row]
        family_scores[family_name] = _mean(values)
    return family_scores


def _compute_transformed_component_score(
    component_category: str,
    family_scores: dict[str, float],
) -> float:
    """Calcula o score do componente transformado."""

    if component_category in family_scores:
        return family_scores[component_category]
    if component_category == "Combinações":
        return _mean(list(family_scores.values()))
    return _mean(list(family_scores.values()))


def _build_pair_observation(
    pair_type: str,
    component_category: str,
    metadata: TransformationMetadataRecord | None,
    family_scores: dict[str, float],
    weighted_average: float,
    transformed_component_score: float,
) -> str:
    """Gera uma observacao automatica para um par."""

    if pair_type != "positive" or component_category == "Não aplicável":
        return "Par de controle negativo; usado como referência de não transformação."

    impacts = {
        family: 1.0 - score
        for family, score in family_scores.items()
    }
    most_sensitive_family = max(impacts, key=impacts.get)
    most_stable_family = min(impacts, key=impacts.get)
    sensitive_components = (
        metadata.transformed_components if metadata is not None else (component_category,)
    )
    if component_category == "Combinações":
        expected_fragment = ", ".join(sensitive_components)
    else:
        expected_fragment = component_category

    observations = [
        f"Maior sensibilidade observada em {most_sensitive_family.lower()}.",
        f"Componente transformado: {expected_fragment}.",
        f"Maior estabilidade em {most_stable_family.lower()}.",
    ]

    if most_sensitive_family == component_category or (
        component_category == "Combinações"
        and most_sensitive_family in sensitive_components
    ):
        observations.append("O componente transformado foi capturado pela familia mais sensivel.")
    else:
        observations.append("A familia mais sensivel não coincidiu exatamente com o componente transformado.")

    global_distance = abs(weighted_average - transformed_component_score)
    if global_distance <= 0.05:
        observations.append("A métrica global permaneceu coerente com o componente transformado.")
    elif weighted_average >= transformed_component_score:
        observations.append("A métrica global ficou acima do componente transformado.")
    else:
        observations.append("A métrica global ficou abaixo do componente transformado.")

    return " ".join(observations)


def _build_category_stats(
    category: str,
    records: list[PairInterpretabilityRecord],
) -> CategoryInterpretabilityStats:
    """Calcula estatisticas resumidas para uma categoria."""

    target_values = [record.transformed_component_score for record in records]
    global_values = [record.score_global for record in records]
    gap_values = [record.score_gap for record in records]
    return CategoryInterpretabilityStats(
        category=category,
        pair_count=len(records),
        target_mean=_mean(target_values),
        target_median=_median(target_values),
        target_std=_std(target_values),
        target_min=min(target_values) if target_values else 0.0,
        target_max=max(target_values) if target_values else 0.0,
        global_mean=_mean(global_values),
        global_median=_median(global_values),
        global_std=_std(global_values),
        global_min=min(global_values) if global_values else 0.0,
        global_max=max(global_values) if global_values else 0.0,
        gap_mean=_mean(gap_values),
        gap_median=_median(gap_values),
        gap_std=_std(gap_values),
        gap_min=min(gap_values) if gap_values else 0.0,
        gap_max=max(gap_values) if gap_values else 0.0,
    )


def _build_category_evidence(
    category: str,
    records: list[PairInterpretabilityRecord],
) -> CategoryEvidence:
    """Gera evidencias interpretativas agregadas."""

    family_average_impact: dict[str, float] = {}
    family_std_impact: dict[str, float] = {}
    family_similarity_means: dict[str, float] = {}
    attribute_map = {
        "Melodia": "score_melody",
        "Harmonia": "score_harmony",
        "Ritmo": "score_rhythm",
    }
    for family_name in FAMILY_COLUMNS:
        similarity_values = [
            getattr(record, attribute_map[family_name]) for record in records
        ]
        values = [1.0 - value for value in similarity_values]
        family_average_impact[family_name] = _mean(values)
        family_std_impact[family_name] = _std(values)
        family_similarity_means[family_name] = _mean(similarity_values)

    most_sensitive_family = max(family_average_impact, key=family_average_impact.get)
    most_stable_family = min(family_average_impact, key=family_average_impact.get)
    most_variable_family = max(family_std_impact, key=family_std_impact.get)

    target_mean = _mean([record.transformed_component_score for record in records])
    simple_average_mean = _mean([record.simple_average for record in records])
    weighted_average_mean = _mean([record.weighted_average for record in records])
    if abs(weighted_average_mean - target_mean) <= 0.05:
        global_behavior = (
            "A métrica global acompanhou de perto o componente transformado."
        )
    elif weighted_average_mean > target_mean:
        global_behavior = "A métrica global permaneceu mais conservadora que as métricas específicas."
    else:
        global_behavior = "A métrica global refletiu uma queda mais forte que o componente transformado."

    return CategoryEvidence(
        category=category,
        most_sensitive_family=most_sensitive_family,
        most_stable_family=most_stable_family,
        most_variable_family=most_variable_family,
        global_behavior=global_behavior,
        family_similarity_means=family_similarity_means,
        simple_average_mean=simple_average_mean,
        weighted_average_mean=weighted_average_mean,
    )


def _mean(values: list[float]) -> float:
    """Calcula a media de uma lista de valores."""

    if not values:
        return 0.0
    return statistics.fmean(values)


def _median(values: list[float]) -> float:
    """Calcula a mediana de uma lista de valores."""

    if not values:
        return 0.0
    return statistics.median(values)


def _std(values: list[float]) -> float:
    """Calcula o desvio padrao populacional."""

    if len(values) <= 1:
        return 0.0
    return statistics.pstdev(values)


def _load_json_field(value: Any) -> dict[str, Any]:
    """Converte um campo JSON textual em dicionario."""

    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip():
        loaded = json.loads(value)
        if isinstance(loaded, dict):
            return loaded
    return {}


def _resolve_path(value: str) -> Path:
    """Resolve um caminho serializado no JSON."""

    path = Path(value)
    if path.is_absolute():
        return path
    return Path.cwd() / path


def _write_csv(csv_path: Path, rows: list[PairInterpretabilityRecord]) -> None:
    """Escreve o CSV consolidado da interpretabilidade."""

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "pair_id",
                "pair_type",
                "transformation",
                "component_transformed",
                "score_melody",
                "score_harmony",
                "score_rhythm",
                "simple_average",
                "weighted_average",
                "score_global",
                "score_gap",
                "transformed_component_score",
                "global_delta",
                "observations",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "pair_id": row.pair_id,
                    "pair_type": row.pair_type,
                    "transformation": row.transformation,
                    "component_transformed": row.component_transformed,
                    "score_melody": f"{row.score_melody:.6f}",
                    "score_harmony": f"{row.score_harmony:.6f}",
                    "score_rhythm": f"{row.score_rhythm:.6f}",
                    "simple_average": f"{row.simple_average:.6f}",
                    "weighted_average": f"{row.weighted_average:.6f}",
                    "score_global": f"{row.score_global:.6f}",
                    "score_gap": f"{row.score_gap:.6f}",
                    "transformed_component_score": f"{row.transformed_component_score:.6f}",
                    "global_delta": f"{row.global_delta:.6f}",
                    "observations": row.observations,
                }
            )


def _write_json(json_path: Path, payload: dict[str, Any]) -> None:
    """Escreve o JSON consolidado da interpretabilidade."""

    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _write_report(
    report_path: Path,
    summary: InterpretabilitySummary,
    category_stats: list[CategoryInterpretabilityStats],
    category_evidence: list[CategoryEvidence],
) -> None:
    """Escreve o relatorio Markdown da interpretabilidade."""

    lines = [
        "# Relatório de Interpretabilidade das Métricas",
        "",
        f"Data: {summary.inspection_date.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Resumo da avaliação",
        "",
        f"- Pares positivos: {summary.positive_pairs}",
        f"- Pares negativos: {summary.negative_pairs}",
        f"- Categorias de transformação: {summary.transformation_categories}",
        f"- Tempo de execução: {summary.execution_time_seconds:.3f} segundos",
        "",
        "## Estatísticas por tipo de transformação",
        "",
        "| Categoria | Pares | Média alvo | Mediana alvo | DP alvo | Mín alvo | Máx alvo | Média global | Mediana global | DP global | Mín global | Máx global | Média da diferença |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for stats in category_stats:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_markdown(stats.category),
                    str(stats.pair_count),
                    f"{stats.target_mean:.6f}",
                    f"{stats.target_median:.6f}",
                    f"{stats.target_std:.6f}",
                    f"{stats.target_min:.6f}",
                    f"{stats.target_max:.6f}",
                    f"{stats.global_mean:.6f}",
                    f"{stats.global_median:.6f}",
                    f"{stats.global_std:.6f}",
                    f"{stats.global_min:.6f}",
                    f"{stats.global_max:.6f}",
                    f"{stats.gap_mean:.6f}",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Comparação entre métricas individuais e métrica global",
            "",
            "| Categoria | Melodia | Harmonia | Ritmo | Média simples | Média ponderada |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    evidence_by_category = {evidence.category: evidence for evidence in category_evidence}
    for stats in category_stats:
        evidence = evidence_by_category[stats.category]
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_markdown(stats.category),
                    f"{evidence.family_similarity_means['Melodia']:.6f}",
                    f"{evidence.family_similarity_means['Harmonia']:.6f}",
                    f"{evidence.family_similarity_means['Ritmo']:.6f}",
                    f"{evidence.simple_average_mean:.6f}",
                    f"{evidence.weighted_average_mean:.6f}",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Evidências interpretativas",
            "",
        ]
    )
    for evidence in category_evidence:
        lines.append(f"### {evidence.category}")
        lines.append("")
        lines.append(f"- Métrica mais sensível: {evidence.most_sensitive_family}")
        lines.append(f"- Métrica mais estável: {evidence.most_stable_family}")
        lines.append(f"- Maior variação: {evidence.most_variable_family}")
        lines.append(f"- Comportamento da métrica global: {evidence.global_behavior}")
        lines.append("")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_cache(
    cache_path: Path,
    fingerprint: str,
    csv_path: Path,
    json_path: Path,
    report_path: Path,
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

    if (
        not cache_path.is_file()
        or not csv_path.is_file()
        or not json_path.is_file()
        or not report_path.is_file()
    ):
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
    print("Resultados de interpretabilidade reutilizados a partir do cache.")
    print(f"CSV: {csv_path.as_posix()}")
    print(f"JSON: {json_path.as_posix()}")
    print(f"Markdown: {report_path.as_posix()}")
    print(f"Total de pares: {cached_payload.get('total_pairs', 0)}")
    print(f"Pares positivos: {cached_payload.get('positive_pairs', 0)}")
    print(f"Pares negativos: {cached_payload.get('negative_pairs', 0)}")


def _print_summary(
    summary: InterpretabilitySummary,
    report_path: Path,
    category_stats: list[CategoryInterpretabilityStats],
    category_evidence: list[CategoryEvidence],
) -> None:
    """Exibe um resumo amigavel da avaliacao."""

    print("Avaliacao de interpretabilidade concluida.")
    print(f"Pares processados: {summary.total_pairs}")
    print(f"Pares positivos: {summary.positive_pairs}")
    print(f"Pares negativos: {summary.negative_pairs}")
    print(f"Categorias analisadas: {summary.transformation_categories}")
    print(f"Estatisticas geradas: {len(category_stats)}")
    print(f"Evidencias geradas: {len(category_evidence)}")
    print(f"Tempo de execução: {summary.execution_time_seconds:.3f} segundos")
    print(f"Relatório gerado em: {report_path.as_posix()}")


def _compute_fingerprint(
    pairs_path: Path,
    results_path: Path,
    transformations_root: Path,
) -> str:
    """Gera uma assinatura estavel dos arquivos utilizados."""

    digest = hashlib.sha256()
    digest.update(pairs_path.read_bytes())
    digest.update(results_path.read_bytes())
    for metadata_path in sorted(
        path
        for path in transformations_root.rglob("metadata.csv")
        if "validation" not in path.parts and "experiment" not in path.parts
    ):
        digest.update(metadata_path.as_posix().encode("utf-8"))
        digest.update(metadata_path.read_bytes())
    return digest.hexdigest()


def _escape_markdown(value: str) -> str:
    """Escapa barras verticais em tabelas Markdown."""

    return value.replace("|", "\\|")
