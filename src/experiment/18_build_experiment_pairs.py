"""Pipeline para formação dos pares experimentais."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import csv
import hashlib
import json
from pathlib import Path
import random
import time
from typing import Any


@dataclass(frozen=True)
class RepresentationEntry:
    """Representa uma representação disponível para compor pares."""

    song_id: str
    segment_id: str
    representation_path: Path
    transformation: str
    transformation_parameters: dict[str, Any]
    source_kind: str


@dataclass(frozen=True)
class ExperimentPair:
    """Representa um par experimental."""

    pair_id: str
    pair_type: str
    original_song_id: str
    original_segment_id: str
    comparison_song_id: str
    comparison_segment_id: str
    original_representation: Path
    comparison_representation: Path
    transformation: str | None = None
    transformation_parameters: dict[str, Any] | None = None


@dataclass(frozen=True)
class ExperimentPairSummary:
    """Resumo da formação dos pares experimentais."""

    source_path: Path
    transformations_path: Path
    output_path: Path
    inspection_date: datetime
    execution_time_seconds: float
    positives_found: int
    negatives_generated: int
    total_pairs: int
    seed: int
    fingerprint: str


def build_experiment_pairs(
    representations_path: str | Path,
    transformations_path: str | Path,
    output_path: str | Path,
    random_seed: int,
) -> Path:
    """Forma pares positivos e negativos a partir das representações existentes."""

    representations_root = Path(representations_path)
    transformations_root = Path(transformations_path)
    output_root = Path(output_path)
    inspection_date = datetime.now()
    start_time = time.perf_counter()

    if not representations_root.is_dir():
        raise FileNotFoundError(
            f"Diretório de representações não encontrado: {representations_root}"
        )
    if not transformations_root.is_dir():
        raise FileNotFoundError(
            f"Diretório de transformações não encontrado: {transformations_root}"
        )

    source_fingerprint = _compute_fingerprint(
        representations_root=representations_root,
        transformations_root=transformations_root,
        random_seed=random_seed,
    )
    output_root.mkdir(parents=True, exist_ok=True)
    csv_path = output_root / "experiment_pairs.csv"
    json_path = output_root / "experiment_pairs.json"
    cache_path = output_root / "experiment_pairs_cache.json"

    if _is_cache_valid(cache_path, csv_path, json_path, source_fingerprint):
        _print_cache_summary(cache_path, csv_path, json_path)
        return output_root

    print("Iniciando a formação dos pares experimentais...")

    original_entries = _load_original_entries(representations_root)
    transformed_entries = _load_transformed_entries(
        transformations_root=transformations_root,
        representations_root=representations_root,
    )
    positive_pairs = _build_positive_pairs(
        original_entries=original_entries,
        transformed_entries=transformed_entries,
    )
    if not positive_pairs:
        raise ValueError(
            "Não foram encontrados pares positivos suficientes para formar o conjunto experimental."
        )
    negative_pairs = _build_negative_pairs(
        positive_pairs=positive_pairs,
        candidate_entries=original_entries + transformed_entries,
        random_seed=random_seed,
    )

    if len(negative_pairs) < len(positive_pairs):
        raise ValueError(
            "Não foi possível balancear os pares experimentais com os candidatos disponíveis."
        )

    negative_pairs = negative_pairs[: len(positive_pairs)]
    all_pairs = positive_pairs + negative_pairs
    all_pairs = _assign_pair_ids(all_pairs)

    _write_csv(csv_path, all_pairs)
    _write_json(
        json_path,
        summary={
            "seed": random_seed,
            "fingerprint": source_fingerprint,
            "generated_at": inspection_date.isoformat(),
            "positives_found": len(positive_pairs),
            "negatives_generated": len(negative_pairs),
            "total_pairs": len(all_pairs),
            "pairs": [_pair_to_dict(pair) for pair in all_pairs],
        },
    )
    _write_csv(output_root.parent / "experiment_pairs.csv", all_pairs)
    _write_json(
        output_root.parent / "experiment_pairs.json",
        summary={
            "seed": random_seed,
            "fingerprint": source_fingerprint,
            "generated_at": inspection_date.isoformat(),
            "positives_found": len(positive_pairs),
            "negatives_generated": len(negative_pairs),
            "total_pairs": len(all_pairs),
            "pairs": [_pair_to_dict(pair) for pair in all_pairs],
        },
    )
    _write_cache(
        cache_path=cache_path,
        fingerprint=source_fingerprint,
        seed=random_seed,
        csv_path=csv_path,
        json_path=json_path,
        total_pairs=len(all_pairs),
    )

    summary = ExperimentPairSummary(
        source_path=representations_root,
        transformations_path=transformations_root,
        output_path=output_root,
        inspection_date=inspection_date,
        execution_time_seconds=time.perf_counter() - start_time,
        positives_found=len(positive_pairs),
        negatives_generated=len(negative_pairs),
        total_pairs=len(all_pairs),
        seed=random_seed,
        fingerprint=source_fingerprint,
    )
    _print_summary(summary, csv_path, json_path)
    return output_root


def _load_original_entries(representations_root: Path) -> list[RepresentationEntry]:
    """Carrega as representações originais extraídas."""

    entries: list[RepresentationEntry] = []
    for json_path in sorted(representations_root.glob("*.json")):
        song_id, segment_id = _parse_segment_identifier(json_path.stem)
        entries.append(
            RepresentationEntry(
                song_id=song_id,
                segment_id=segment_id,
                representation_path=json_path,
                transformation="original",
                transformation_parameters={},
                source_kind="original",
            )
        )
    return entries


def _load_transformed_entries(
    transformations_root: Path,
    representations_root: Path,
) -> list[RepresentationEntry]:
    """Carrega as representações transformadas já geradas."""

    entries: list[RepresentationEntry] = []
    metadata_files = sorted(
        path
        for path in transformations_root.rglob("metadata.csv")
        if "validation" not in path.parts and "experiment" not in path.parts
    )
    for metadata_path in metadata_files:
        metadata_rows = _read_csv(metadata_path)
        for row in metadata_rows:
            song_id = row.get("song_id", "")
            segment_id = row.get("segment_id", "")
            generated_file = metadata_path.parent / row["generated_file"]
            source_file = representations_root / row["source_file"]
            entries.append(
                RepresentationEntry(
                    song_id=song_id,
                    segment_id=segment_id,
                    representation_path=generated_file,
                    transformation=row.get("transformation", ""),
                    transformation_parameters=_load_json_field(
                        row.get("parameters", "{}")
                    ),
                    source_kind="transformed",
                )
            )
            if not source_file.is_file():
                raise FileNotFoundError(
                    f"Representação original referenciada não encontrada: {source_file}"
                )
            if not generated_file.is_file():
                raise FileNotFoundError(
                    f"Representação transformada referenciada não encontrada: {generated_file}"
                )
    return entries


def _build_positive_pairs(
    original_entries: list[RepresentationEntry],
    transformed_entries: list[RepresentationEntry],
) -> list[ExperimentPair]:
    """Gera os pares positivos a partir de origem e transformação."""

    original_lookup = {
        entry.representation_path.name: entry for entry in original_entries
    }
    pairs: list[ExperimentPair] = []

    for transformed_entry in sorted(
        transformed_entries,
        key=lambda entry: (
            entry.song_id,
            entry.segment_id,
            entry.transformation,
            entry.representation_path.as_posix(),
        ),
    ):
        source_name = f"{transformed_entry.song_id}_segment_{transformed_entry.segment_id}.json"
        original_entry = original_lookup.get(source_name)
        if original_entry is None:
            continue

        pairs.append(
            ExperimentPair(
                pair_id="",
                pair_type="positive",
                original_song_id=original_entry.song_id,
                original_segment_id=original_entry.segment_id,
                comparison_song_id=transformed_entry.song_id,
                comparison_segment_id=transformed_entry.segment_id,
                original_representation=original_entry.representation_path,
                comparison_representation=transformed_entry.representation_path,
                transformation=transformed_entry.transformation,
                transformation_parameters=transformed_entry.transformation_parameters,
            )
        )
    return pairs


def _build_negative_pairs(
    positive_pairs: list[ExperimentPair],
    candidate_entries: list[RepresentationEntry],
    random_seed: int,
) -> list[ExperimentPair]:
    """Gera pares negativos distintos e reprodutíveis."""

    rng = random.Random(random_seed)
    candidates = sorted(
        candidate_entries,
        key=lambda entry: (
            entry.song_id,
            entry.segment_id,
            entry.source_kind,
            entry.transformation,
            entry.representation_path.as_posix(),
        ),
    )
    negative_pairs: list[ExperimentPair] = []
    seen_pairs: set[tuple[str, str, str, str, str]] = set()

    for positive in positive_pairs:
        eligible_candidates = [
            candidate
            for candidate in candidates
            if candidate.song_id != positive.original_song_id
        ]
        if not eligible_candidates:
            continue

        shuffled_candidates = eligible_candidates[:]
        rng.shuffle(shuffled_candidates)
        chosen_candidate = None
        for candidate in shuffled_candidates:
            pair_key = (
                "negative",
                positive.original_representation.as_posix(),
                candidate.representation_path.as_posix(),
                positive.original_song_id,
                candidate.song_id,
            )
            if pair_key in seen_pairs:
                continue
            chosen_candidate = candidate
            seen_pairs.add(pair_key)
            break

        if chosen_candidate is None:
            continue

        negative_pairs.append(
            ExperimentPair(
                pair_id="",
                pair_type="negative",
                original_song_id=positive.original_song_id,
                original_segment_id=positive.original_segment_id,
                comparison_song_id=chosen_candidate.song_id,
                comparison_segment_id=chosen_candidate.segment_id,
                original_representation=positive.original_representation,
                comparison_representation=chosen_candidate.representation_path,
                transformation=None,
                transformation_parameters=None,
            )
        )

    return negative_pairs


def _assign_pair_ids(pairs: list[ExperimentPair]) -> list[ExperimentPair]:
    """Atribui identificadores estáveis aos pares."""

    order_map = {"positive": 0, "negative": 1}
    ordered_pairs = sorted(
        pairs,
        key=lambda pair: (
            order_map.get(pair.pair_type, 99),
            pair.original_song_id,
            pair.original_segment_id,
            pair.comparison_song_id,
            pair.comparison_segment_id,
            pair.transformation or "",
            _json_sort_key(pair.transformation_parameters or {}),
        ),
    )
    return [
        ExperimentPair(
            pair_id=f"pair_{index:06d}",
            pair_type=pair.pair_type,
            original_song_id=pair.original_song_id,
            original_segment_id=pair.original_segment_id,
            comparison_song_id=pair.comparison_song_id,
            comparison_segment_id=pair.comparison_segment_id,
            original_representation=pair.original_representation,
            comparison_representation=pair.comparison_representation,
            transformation=pair.transformation,
            transformation_parameters=pair.transformation_parameters,
        )
        for index, pair in enumerate(ordered_pairs, start=1)
    ]


def _write_csv(csv_path: Path, pairs: list[ExperimentPair]) -> None:
    """Escreve os pares em CSV."""

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
                "original_representation",
                "comparison_representation",
            ],
        )
        writer.writeheader()
        writer.writerows(
            {
                "pair_id": pair.pair_id,
                "pair_type": pair.pair_type,
                "original_song_id": pair.original_song_id,
                "original_segment_id": pair.original_segment_id,
                "comparison_song_id": pair.comparison_song_id,
                "comparison_segment_id": pair.comparison_segment_id,
                "transformation": pair.transformation or "",
                "original_representation": pair.original_representation.as_posix(),
                "comparison_representation": pair.comparison_representation.as_posix(),
            }
            for pair in pairs
        )


def _write_json(json_path: Path, summary: dict[str, Any]) -> None:
    """Escreve o JSON com os pares e metadados de reprodução."""

    json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _pair_paths_to_strings(pair: ExperimentPair) -> dict[str, str]:
    """Converte caminhos do par para strings serializáveis."""

    return {
        "original_representation": pair.original_representation.as_posix(),
        "comparison_representation": pair.comparison_representation.as_posix(),
    }


def _pair_to_dict(pair: ExperimentPair) -> dict[str, Any]:
    """Converte um par experimental para um dicionário serializável."""

    payload = asdict(pair)
    payload["original_representation"] = pair.original_representation.as_posix()
    payload["comparison_representation"] = pair.comparison_representation.as_posix()
    return payload


def _write_cache(
    cache_path: Path,
    fingerprint: str,
    seed: int,
    csv_path: Path,
    json_path: Path,
    total_pairs: int,
) -> None:
    """Escreve o cache de reuso."""

    payload = {
        "fingerprint": fingerprint,
        "seed": seed,
        "csv_path": csv_path.as_posix(),
        "json_path": json_path.as_posix(),
        "total_pairs": total_pairs,
    }
    cache_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _is_cache_valid(
    cache_path: Path,
    csv_path: Path,
    json_path: Path,
    fingerprint: str,
) -> bool:
    """Verifica se os arquivos podem ser reutilizados."""

    if not cache_path.is_file() or not csv_path.is_file() or not json_path.is_file():
        return False
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    return payload.get("fingerprint") == fingerprint


def _print_cache_summary(cache_path: Path, csv_path: Path, json_path: Path) -> None:
    """Exibe um resumo quando os pares são reutilizados do cache."""

    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    print("Pares experimentais reutilizados a partir do cache.")
    print(f"CSV: {csv_path.as_posix()}")
    print(f"JSON: {json_path.as_posix()}")
    print(f"Total de pares: {payload.get('total_pairs', 0)}")


def _read_csv(metadata_path: Path) -> list[dict[str, str]]:
    """Lê um CSV de metadados."""

    with metadata_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def _parse_segment_identifier(segment_stem: str) -> tuple[str, str]:
    """Extrai song_id e segment_id a partir do nome do arquivo."""

    parts = segment_stem.split("_segment_")
    if len(parts) != 2:
        return segment_stem, segment_stem
    return parts[0], parts[1]


def _load_json_field(value: Any) -> dict[str, Any]:
    """Converte um campo JSON textual em dicionário."""

    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip():
        loaded = json.loads(value)
        if isinstance(loaded, dict):
            return loaded
    return {}


def _json_sort_key(value: dict[str, Any]) -> str:
    """Cria uma chave estável para ordenação de JSON."""

    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _compute_fingerprint(
    representations_root: Path,
    transformations_root: Path,
    random_seed: int,
) -> str:
    """Gera uma assinatura estável do conteúdo de entrada e da seed."""

    digest = hashlib.sha256()
    digest.update(str(random_seed).encode("utf-8"))

    for root in (representations_root, transformations_root):
        for file_path in sorted(
            path
            for path in root.rglob("*")
            if path.is_file() and path.suffix.lower() in {".json", ".csv"}
            and "experiment" not in path.parts
        ):
            digest.update(file_path.as_posix().encode("utf-8"))
            digest.update(file_path.read_bytes())

    return digest.hexdigest()


def _print_summary(
    summary: ExperimentPairSummary,
    csv_path: Path,
    json_path: Path,
) -> None:
    """Exibe um resumo amigável da formação dos pares."""

    print("Formação dos pares experimentais concluída.")
    print(f"Origem: {summary.source_path.as_posix()}")
    print(f"Transformações: {summary.transformations_path.as_posix()}")
    print(f"Saída: {summary.output_path.as_posix()}")
    print(f"Seed utilizada: {summary.seed}")
    print(f"Pares positivos: {summary.positives_found}")
    print(f"Pares negativos: {summary.negatives_generated}")
    print(f"Total de pares: {summary.total_pairs}")
    print(f"CSV gerado em: {csv_path.as_posix()}")
    print(f"JSON gerado em: {json_path.as_posix()}")
    print(f"Tempo de execução: {summary.execution_time_seconds:.3f} segundos")
