"""Pipeline para execução das métricas de similaridade sobre pares experimentais."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import csv
import hashlib
import importlib
import json
from pathlib import Path
import time
from typing import Any, Mapping

from metrics.harmony import (
    ChordNGramSimilarityMetric,
    HarmonicEditDistanceMetric,
    PitchClassSimilarityMetric,
)
from metrics.melody import (
    EditDistanceMetric,
    IntervalNGramSimilarityMetric,
    LongestCommonSubsequenceMetric,
)
from metrics.rhythm import (
    IoISimilarityMetric,
    RhythmNGramSimilarityMetric,
    RhythmicEditDistanceMetric,
)
from preprocessing.representation.combined_representation import CombinedRepresentation


validate_weights = importlib.import_module(
    "metrics.global._helpers"
).validate_weights
SimpleAverageMetric = importlib.import_module(
    "metrics.global.simple_average"
).SimpleAverageMetric
WeightedAverageMetric = importlib.import_module(
    "metrics.global.weighted_average"
).WeightedAverageMetric


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
class SimilarityExperimentResult:
    """Resultado completo da avaliação de similaridade de um par."""

    pair_id: str
    pair_type: str
    original_song_id: str
    original_segment_id: str
    comparison_song_id: str
    comparison_segment_id: str
    transformation: str
    original_representation: Path
    comparison_representation: Path
    melody_scores: dict[str, float]
    harmony_scores: dict[str, float]
    rhythm_scores: dict[str, float]
    simple_average: float
    weighted_average: float


@dataclass(frozen=True)
class SimilarityExperimentSummary:
    """Resumo da execução do experimento de similaridade."""

    pairs_path: Path
    output_path: Path
    inspection_date: datetime
    execution_time_seconds: float
    pairs_processed: int
    positive_pairs: int
    negative_pairs: int
    total_comparisons: int
    fingerprint: str


def run_similarity_experiment(
    experiment_pairs_path: str | Path | None = None,
    representations_root: str | Path | None = None,
    output_path: str | Path = "data/results/experiment",
    interval_ngram_n: int = 2,
    chord_ngram_n: int = 2,
    rhythm_ngram_n: int = 2,
    global_weights: Mapping[str, float] | None = None,
) -> Path:
    """Executa todas as métricas sobre os pares experimentais formados."""

    pairs_path = _resolve_pairs_path(experiment_pairs_path)
    output_root = Path(output_path)
    inspection_date = datetime.now()
    start_time = time.perf_counter()

    if not pairs_path.is_file():
        raise FileNotFoundError(
            f"Arquivo de pares experimentais não encontrado: {pairs_path}"
        )

    if global_weights is None:
        global_weights = {"melody": 0.4, "harmony": 0.35, "rhythm": 0.25}
    validated_weights = validate_weights(global_weights)

    output_root.mkdir(parents=True, exist_ok=True)
    csv_path = output_root / "similarity_results.csv"
    json_path = output_root / "similarity_results.json"
    cache_path = output_root / "similarity_results_cache.json"

    fingerprint = _compute_fingerprint(
        pairs_path=pairs_path,
        interval_ngram_n=interval_ngram_n,
        chord_ngram_n=chord_ngram_n,
        rhythm_ngram_n=rhythm_ngram_n,
        weights=validated_weights,
    )

    if _is_cache_valid(cache_path, csv_path, json_path, fingerprint):
        _print_cache_summary(cache_path, csv_path, json_path)
        return output_root

    print("Iniciando a execução das métricas de similaridade...")

    payload = _load_json(pairs_path)
    pair_records = [
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
        for pair in payload.get("pairs", [])
    ]

    melody_interval_metric = IntervalNGramSimilarityMetric()
    melody_lcs_metric = LongestCommonSubsequenceMetric()
    melody_edit_metric = EditDistanceMetric()

    harmony_ngram_metric = ChordNGramSimilarityMetric()
    harmony_edit_metric = HarmonicEditDistanceMetric()
    harmony_pitch_metric = PitchClassSimilarityMetric()

    rhythm_ngram_metric = RhythmNGramSimilarityMetric()
    rhythm_ioi_metric = IoISimilarityMetric()
    rhythm_edit_metric = RhythmicEditDistanceMetric()

    simple_average_metric = SimpleAverageMetric()
    weighted_average_metric = WeightedAverageMetric()

    results: list[SimilarityExperimentResult] = []
    for pair in pair_records:
        original = _load_combined_representation(_resolve_path(pair.original_representation))
        comparison = _load_combined_representation(_resolve_path(pair.comparison_representation))

        melody_scores = {
            "interval_ngram_similarity": melody_interval_metric.compute(
                original.melody,
                comparison.melody,
                n=interval_ngram_n,
            ),
            "lcs_similarity": melody_lcs_metric.compute(original.melody, comparison.melody),
            "edit_distance_similarity": melody_edit_metric.compute(
                original.melody,
                comparison.melody,
            ),
        }
        harmony_scores = {
            "chord_ngram_similarity": harmony_ngram_metric.compute(
                original.harmony,
                comparison.harmony,
                n=chord_ngram_n,
            ),
            "harmonic_edit_distance": harmony_edit_metric.compute(
                original.harmony,
                comparison.harmony,
            ),
            "pitch_class_similarity": harmony_pitch_metric.compute(
                original.harmony,
                comparison.harmony,
            ),
        }
        rhythm_scores = {
            "rhythm_ngram_similarity": rhythm_ngram_metric.compute(
                original.rhythm,
                comparison.rhythm,
                n=rhythm_ngram_n,
            ),
            "ioi_similarity": rhythm_ioi_metric.compute(original.rhythm, comparison.rhythm),
            "rhythmic_edit_distance": rhythm_edit_metric.compute(
                original.rhythm,
                comparison.rhythm,
            ),
        }

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

        results.append(
            SimilarityExperimentResult(
                pair_id=pair.pair_id,
                pair_type=pair.pair_type,
                original_song_id=pair.original_song_id,
                original_segment_id=pair.original_segment_id,
                comparison_song_id=pair.comparison_song_id,
                comparison_segment_id=pair.comparison_segment_id,
                transformation=pair.transformation or "",
                original_representation=_resolve_path(pair.original_representation),
                comparison_representation=_resolve_path(pair.comparison_representation),
                melody_scores=melody_scores,
                harmony_scores=harmony_scores,
                rhythm_scores=rhythm_scores,
                simple_average=simple_average,
                weighted_average=weighted_average,
            )
        )

    _write_csv(csv_path, results, validated_weights)
    _write_json(
        json_path,
        {
            "pairs_path": pairs_path.as_posix(),
            "generated_at": inspection_date.isoformat(),
            "fingerprint": fingerprint,
            "metric_configuration": {
                "melody": {"interval_ngram_n": interval_ngram_n},
                "harmony": {"chord_ngram_n": chord_ngram_n},
                "rhythm": {"rhythm_ngram_n": rhythm_ngram_n},
                "global": {"weights": dict(validated_weights)},
            },
            "results": [_result_to_dict(result, validated_weights) for result in results],
        },
    )
    _write_cache(
        cache_path=cache_path,
        fingerprint=fingerprint,
        csv_path=csv_path,
        json_path=json_path,
        total_pairs=len(results),
        total_comparisons=len(results) * 11,
    )

    summary = SimilarityExperimentSummary(
        pairs_path=pairs_path,
        output_path=output_root,
        inspection_date=inspection_date,
        execution_time_seconds=time.perf_counter() - start_time,
        pairs_processed=len(results),
        positive_pairs=sum(1 for result in results if result.pair_type == "positive"),
        negative_pairs=sum(1 for result in results if result.pair_type == "negative"),
        total_comparisons=len(results) * 11,
        fingerprint=fingerprint,
    )
    _print_summary(summary, csv_path, json_path)
    return output_root


def _resolve_pairs_path(experiment_pairs_path: str | Path | None) -> Path:
    """Resolve o caminho do arquivo de pares experimentais."""

    candidates = _candidate_pairs_paths(experiment_pairs_path)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return candidates[0]


def _candidate_pairs_paths(
    experiment_pairs_path: str | Path | None,
) -> list[Path]:
    """Gera os caminhos candidatos para o arquivo de pares experimentais."""

    default_root = Path("data/results/experiment")
    default_pairs = default_root / "pairs" / "experiment_pairs.json"
    default_file = default_root / "experiment_pairs.json"

    if experiment_pairs_path is None:
        return [default_file, default_pairs]

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
            default_file,
            default_pairs,
        ]

    return [
        path / "experiment_pairs.json",
        path / "pairs" / "experiment_pairs.json",
        default_file,
        default_pairs,
    ]


def _infer_representations_root(pair_records: list[ExperimentPairRecord]) -> Path | None:
    """Infere a raiz das representações a partir do primeiro par disponível."""

    if not pair_records:
        return None
    first_pair = pair_records[0]
    first_path = _resolve_path(first_pair.original_representation)
    if "representations" in first_path.parts:
        index = first_path.parts.index("representations")
        return Path(*first_path.parts[: index + 1])
    return first_path.parent


def _load_combined_representation(path: Path) -> CombinedRepresentation:
    """Carrega uma representação combinada a partir do JSON."""

    if not path.is_file():
        raise FileNotFoundError(
            f"Representação combinada não encontrada: {path}"
        )
    return CombinedRepresentation.from_dict(_load_json(path))


def _resolve_path(value: str) -> Path:
    """Resolve um caminho serializado no JSON."""

    path = Path(value)
    if path.is_absolute():
        return path
    return Path.cwd() / path


def _load_json(path: Path) -> dict[str, Any]:
    """Carrega um JSON do disco."""

    return json.loads(path.read_text(encoding="utf-8"))


def _load_json_field(value: Any) -> dict[str, Any]:
    """Normaliza um campo JSON textual."""

    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip():
        loaded = json.loads(value)
        if isinstance(loaded, dict):
            return loaded
    return {}


def _result_to_dict(
    result: SimilarityExperimentResult,
    weights: Mapping[str, float],
) -> dict[str, Any]:
    """Converte o resultado para dicionário serializável."""

    return {
        "pair_id": result.pair_id,
        "pair_type": result.pair_type,
        "original_song_id": result.original_song_id,
        "original_segment_id": result.original_segment_id,
        "comparison_song_id": result.comparison_song_id,
        "comparison_segment_id": result.comparison_segment_id,
        "transformation": result.transformation,
        "original_representation": result.original_representation.as_posix(),
        "comparison_representation": result.comparison_representation.as_posix(),
        "melody_scores": result.melody_scores,
        "harmony_scores": result.harmony_scores,
        "rhythm_scores": result.rhythm_scores,
        "simple_average": result.simple_average,
        "weighted_average": result.weighted_average,
        "weights_used": dict(weights),
    }


def _write_csv(
    csv_path: Path,
    results: list[SimilarityExperimentResult],
    weights: Mapping[str, float],
) -> None:
    """Escreve os resultados em CSV."""

    with csv_path.open("w", encoding="utf-8", newline="") as file:
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
                "original_representation",
                "comparison_representation",
                "weights_used",
            ],
        )
        writer.writeheader()
        writer.writerows(_flatten_result(result, weights) for result in results)


def _flatten_result(
    result: SimilarityExperimentResult,
    weights: Mapping[str, float],
) -> dict[str, str]:
    """Achata um resultado em uma linha de CSV."""

    return {
        "pair_id": result.pair_id,
        "pair_type": result.pair_type,
        "original_song_id": result.original_song_id,
        "original_segment_id": result.original_segment_id,
        "comparison_song_id": result.comparison_song_id,
        "comparison_segment_id": result.comparison_segment_id,
        "transformation": result.transformation,
        "interval_ngram_similarity": f"{result.melody_scores['interval_ngram_similarity']:.6f}",
        "lcs_similarity": f"{result.melody_scores['lcs_similarity']:.6f}",
        "edit_distance_similarity": f"{result.melody_scores['edit_distance_similarity']:.6f}",
        "chord_ngram_similarity": f"{result.harmony_scores['chord_ngram_similarity']:.6f}",
        "harmonic_edit_distance": f"{result.harmony_scores['harmonic_edit_distance']:.6f}",
        "pitch_class_similarity": f"{result.harmony_scores['pitch_class_similarity']:.6f}",
        "rhythm_ngram_similarity": f"{result.rhythm_scores['rhythm_ngram_similarity']:.6f}",
        "ioi_similarity": f"{result.rhythm_scores['ioi_similarity']:.6f}",
        "rhythmic_edit_distance": f"{result.rhythm_scores['rhythmic_edit_distance']:.6f}",
        "simple_average": f"{result.simple_average:.6f}",
        "weighted_average": f"{result.weighted_average:.6f}",
        "original_representation": result.original_representation.as_posix(),
        "comparison_representation": result.comparison_representation.as_posix(),
        "weights_used": json.dumps(dict(weights), ensure_ascii=False, sort_keys=True),
    }


def _write_json(json_path: Path, payload: dict[str, Any]) -> None:
    """Escreve o JSON consolidado dos resultados."""

    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _write_cache(
    cache_path: Path,
    fingerprint: str,
    csv_path: Path,
    json_path: Path,
    total_pairs: int,
    total_comparisons: int,
) -> None:
    """Escreve o cache de reuso."""

    cache_path.write_text(
        json.dumps(
            {
                "fingerprint": fingerprint,
                "csv_path": csv_path.as_posix(),
                "json_path": json_path.as_posix(),
                "total_pairs": total_pairs,
                "total_comparisons": total_comparisons,
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
    fingerprint: str,
) -> bool:
    """Verifica se os resultados podem ser reutilizados."""

    if not cache_path.is_file() or not csv_path.is_file() or not json_path.is_file():
        return False
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    return payload.get("fingerprint") == fingerprint


def _print_cache_summary(cache_path: Path, csv_path: Path, json_path: Path) -> None:
    """Exibe um resumo quando os resultados são reutilizados."""

    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    print("Resultados de similaridade reutilizados a partir do cache.")
    print(f"CSV: {csv_path.as_posix()}")
    print(f"JSON: {json_path.as_posix()}")
    print(f"Total de pares: {payload.get('total_pairs', 0)}")
    print(f"Total de comparações: {payload.get('total_comparisons', 0)}")


def _compute_fingerprint(
    pairs_path: Path,
    interval_ngram_n: int,
    chord_ngram_n: int,
    rhythm_ngram_n: int,
    weights: Mapping[str, float],
) -> str:
    """Gera uma assinatura estável da configuração e dos pares."""

    digest = hashlib.sha256()
    payload = _load_json(pairs_path)
    normalized_pairs = sorted(
        (
            {
                "pair_id": str(pair.get("pair_id", "")),
                "pair_type": str(pair.get("pair_type", "")),
                "original_song_id": str(pair.get("original_song_id", "")),
                "original_segment_id": str(pair.get("original_segment_id", "")),
                "comparison_song_id": str(pair.get("comparison_song_id", "")),
                "comparison_segment_id": str(pair.get("comparison_segment_id", "")),
                "original_representation": str(pair.get("original_representation", "")),
                "comparison_representation": str(pair.get("comparison_representation", "")),
                "transformation": str(pair.get("transformation", "")),
                "transformation_parameters": pair.get("transformation_parameters", {}),
            }
            for pair in payload.get("pairs", [])
        ),
        key=lambda pair: pair["pair_id"],
    )
    digest.update(
        json.dumps(
            {
                "pairs": normalized_pairs,
                "interval_ngram_n": interval_ngram_n,
                "chord_ngram_n": chord_ngram_n,
                "rhythm_ngram_n": rhythm_ngram_n,
                "weights": dict(weights),
            },
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")
    )
    return digest.hexdigest()


def _print_summary(
    summary: SimilarityExperimentSummary,
    csv_path: Path,
    json_path: Path,
) -> None:
    """Exibe um resumo amigável da execução."""

    print("Execução das métricas de similaridade concluída.")
    print(f"Parâmetros carregados de: {summary.pairs_path.as_posix()}")
    print(f"Saída: {summary.output_path.as_posix()}")
    print(f"Pares processados: {summary.pairs_processed}")
    print(f"Pares positivos: {summary.positive_pairs}")
    print(f"Pares negativos: {summary.negative_pairs}")
    print(f"Total de comparações: {summary.total_comparisons}")
    print(f"CSV gerado em: {csv_path.as_posix()}")
    print(f"JSON gerado em: {json_path.as_posix()}")
    print(f"Tempo de execução: {summary.execution_time_seconds:.3f} segundos")
