"""Pipeline de transformações harmônicas sobre representações extraídas."""

from __future__ import annotations

from dataclasses import dataclass
import csv
import json
from pathlib import Path
import re
from typing import Any

from preprocessing.representation.harmony_representation import HarmonyRepresentation
from transformations.harmony import (
    ChordSubstitutionTransformation,
    ReharmonizationTransformation,
    SimplificationTransformation,
)


@dataclass(frozen=True)
class HarmonyTransformationSummary:
    """Resumo da execução de uma transformação harmônica."""

    source_path: Path
    output_path: Path
    transformation: str
    parameters: dict[str, Any]
    representations_found: int
    representations_created: int
    representations_reused: int
    metadata_path: Path


def transform_harmonies(
    source_path: str | Path,
    output_path: str | Path,
    transformation_name: str,
    parameters: dict[str, Any],
    random_seed: int,
) -> Path:
    """Aplica uma transformação harmônica às representações existentes."""

    source_root = Path(source_path)
    output_root = Path(output_path)
    normalized_transformation_name = transformation_name.lower().strip()

    if not source_root.is_dir():
        raise FileNotFoundError(f"Diretório de origem não encontrado: {source_root}")

    source_files = sorted(
        path
        for path in source_root.iterdir()
        if path.is_file() and path.suffix.lower() == ".json"
    )
    if not source_files:
        raise ValueError("Não há representações para transformar.")

    transformer = _build_transformer(normalized_transformation_name)
    normalized_parameters = dict(parameters)
    normalized_parameters.setdefault("random_seed", random_seed)
    transformation_root = (
        output_root
        / "harmony"
        / normalized_transformation_name
        / _build_parameter_signature(normalized_parameters)
    )
    transformation_root.mkdir(parents=True, exist_ok=True)

    metadata_path = transformation_root / "metadata.csv"
    representations_created = 0
    representations_reused = 0
    metadata_rows: list[dict[str, str]] = []

    print("Iniciando as transformações harmônicas...")

    for source_file in source_files:
        generated_file = transformation_root / f"{source_file.stem}.json"
        if generated_file.exists():
            representations_reused += 1
        else:
            payload = json.loads(source_file.read_text(encoding="utf-8"))
            representation = HarmonyRepresentation.from_dict(payload)
            transformed_representation = _apply_transformation(
                transformer=transformer,
                representation=representation,
                transformation_name=normalized_transformation_name,
                parameters=normalized_parameters,
                random_seed=random_seed,
            )
            _write_json(
                generated_file,
                {
                    **transformed_representation.to_dict(),
                    "transformation": normalized_transformation_name,
                    "parameters": normalized_parameters,
                },
            )
            representations_created += 1

        source_segment_name = source_file.stem + ".mid"
        song_id, segment_id = _parse_segment_identifier(source_segment_name)
        metadata_rows.append(
            {
                "song_id": song_id,
                "segment_id": segment_id,
                "transformation": normalized_transformation_name,
                "parameters": json.dumps(
                    normalized_parameters, ensure_ascii=False, sort_keys=True
                ),
                "source_file": str(source_file.relative_to(source_root)),
                "generated_file": str(generated_file.relative_to(transformation_root)),
            }
        )

    _write_metadata_csv(metadata_path, metadata_rows)

    summary = HarmonyTransformationSummary(
        source_path=source_root,
        output_path=transformation_root,
        transformation=normalized_transformation_name,
        parameters=normalized_parameters,
        representations_found=len(source_files),
        representations_created=representations_created,
        representations_reused=representations_reused,
        metadata_path=metadata_path,
    )
    _print_summary(summary)
    return transformation_root


def _build_transformer(transformation_name: str) -> object:
    """Cria o transformador solicitado."""

    transform = transformation_name.lower().strip()
    if transform == "chord_substitution":
        return ChordSubstitutionTransformation()
    if transform == "reharmonization":
        return ReharmonizationTransformation()
    if transform == "simplification":
        return SimplificationTransformation()
    raise ValueError(f"Transformação harmônica não suportada: {transformation_name}")


def _apply_transformation(
    transformer: object,
    representation: HarmonyRepresentation,
    transformation_name: str,
    parameters: dict[str, Any],
    random_seed: int,
) -> HarmonyRepresentation:
    """Aplica a transformação selecionada a uma representação."""

    if transformation_name == "chord_substitution":
        strength = float(parameters["strength"])
        return transformer.transform(  # type: ignore[attr-defined]
            representation,
            strength=strength,
            random_seed=random_seed,
        )
    if transformation_name == "reharmonization":
        strength = float(parameters["strength"])
        return transformer.transform(  # type: ignore[attr-defined]
            representation,
            strength=strength,
            random_seed=random_seed,
        )
    if transformation_name == "simplification":
        strength = float(parameters["strength"])
        return transformer.transform(  # type: ignore[attr-defined]
            representation,
            strength=strength,
            random_seed=random_seed,
        )
    raise ValueError(f"Transformação harmônica não suportada: {transformation_name}")


def _parse_segment_identifier(segment_file: str) -> tuple[str, str]:
    """Separa o identificador da música e do segmento."""

    stem = Path(segment_file).stem
    match = re.match(r"^(?P<song_id>.+)_segment_(?P<segment_id>\d+)$", stem)
    if match is None:
        return stem, stem
    return match.group("song_id"), match.group("segment_id")


def _build_parameter_signature(parameters: dict[str, Any]) -> str:
    """Cria um identificador textual para os parâmetros utilizados."""

    ordered_items = sorted(parameters.items())
    parts = [f"{key}_{_normalize_parameter_value(value)}" for key, value in ordered_items]
    return "__".join(parts)


def _normalize_parameter_value(value: Any) -> str:
    """Normaliza valores de parâmetros para uso em caminho de arquivo."""

    if isinstance(value, float):
        return f"{value}".replace(".", "p")
    return str(value)


def _write_json(json_path: Path, payload: dict[str, object]) -> None:
    """Escreve um JSON com a representação transformada."""

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def _write_metadata_csv(metadata_path: Path, rows: list[dict[str, str]]) -> None:
    """Escreve o CSV de metadados da transformação."""

    with metadata_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "song_id",
                "segment_id",
                "transformation",
                "parameters",
                "source_file",
                "generated_file",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def _print_summary(summary: HarmonyTransformationSummary) -> None:
    """Exibe um resumo amigável da transformação harmônica."""

    print("Transformações harmônicas concluídas.")
    print(f"Origem: {summary.source_path.as_posix()}")
    print(f"Saída: {summary.output_path.as_posix()}")
    print(f"Transformação: {summary.transformation}")
    print(f"Representações encontradas: {summary.representations_found}")
    print(f"Representações criadas: {summary.representations_created}")
    print(f"Representações reutilizadas: {summary.representations_reused}")
    print(f"Metadados gerados em: {summary.metadata_path.as_posix()}")