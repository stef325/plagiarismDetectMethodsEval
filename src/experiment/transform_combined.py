"""Pipeline de transformações combinadas sobre representações extraídas."""

from __future__ import annotations

from dataclasses import dataclass
import csv
import json
from pathlib import Path
import re
from typing import Any

from preprocessing.representation.combined_representation import CombinedRepresentation
from transformations.combined import (
    HarmonyRhythmTransformation,
    MelodyHarmonyRhythmTransformation,
    MelodyHarmonyTransformation,
    MelodyRhythmTransformation,
)
from transformations.combined._helpers import build_combination_signature


SUPPORTED_COMBINATIONS = {
    "melody_harmony": MelodyHarmonyTransformation,
    "melody_rhythm": MelodyRhythmTransformation,
    "harmony_rhythm": HarmonyRhythmTransformation,
    "melody_harmony_rhythm": MelodyHarmonyRhythmTransformation,
}


@dataclass(frozen=True)
class CombinedTransformationSummary:
    """Resumo da execução de transformações combinadas."""

    source_path: Path
    output_path: Path
    combinations_found: int
    representations_created: int
    representations_reused: int
    metadata_paths: tuple[Path, ...]


def transform_combined(
    source_path: str | Path,
    output_path: str | Path,
    transformation_section: dict[str, Any],
) -> Path:
    """Aplica combinações de transformações às representações existentes."""

    source_root = Path(source_path)
    output_root = Path(output_path)

    if not source_root.is_dir():
        raise FileNotFoundError(f"Diretório de origem não encontrado: {source_root}")

    source_files = sorted(
        path
        for path in source_root.iterdir()
        if path.is_file() and path.suffix.lower() == ".json"
    )
    if not source_files:
        raise ValueError("Não há representações para transformar.")

    combined_root = output_root / "combined"
    combined_root.mkdir(parents=True, exist_ok=True)

    enabled_combinations = _get_enabled_combinations(transformation_section)
    random_seed = int(transformation_section["random_seed"])
    representations_created = 0
    representations_reused = 0
    metadata_paths: list[Path] = []

    print("Iniciando as transformações combinadas...")

    for combination_name in enabled_combinations:
        combination_spec = _get_combination_spec(transformation_section, combination_name)
        combination_root = (
            combined_root
            / combination_name
            / build_combination_signature(combination_name, combination_spec)
        )
        combination_root.mkdir(parents=True, exist_ok=True)
        metadata_path = combination_root / "metadata.csv"
        metadata_paths.append(metadata_path)

        transformer = _build_transformer(combination_name)
        metadata_rows: list[dict[str, str]] = []

        for source_file in source_files:
            generated_file = combination_root / f"{source_file.stem}.json"
            if generated_file.exists():
                representations_reused += 1
            else:
                payload = json.loads(source_file.read_text(encoding="utf-8"))
                representation = CombinedRepresentation.from_dict(payload)
                transformed_representation = _apply_transformation(
                    transformer=transformer,
                    representation=representation,
                    combination_name=combination_name,
                    combination_spec=combination_spec,
                    random_seed=random_seed,
                )
                _write_json(
                    generated_file,
                    {
                        **transformed_representation.to_dict(),
                        "combination": combination_name,
                        "individual_transformations": _build_individual_transformations(
                            combination_spec
                        ),
                        "parameters": combination_spec,
                    },
                )
                representations_created += 1

            song_id, segment_id = _parse_segment_identifier(source_file.stem + ".mid")
            metadata_rows.append(
                {
                    "song_id": song_id,
                    "segment_id": segment_id,
                    "combination": combination_name,
                    "individual_transformations": json.dumps(
                        _build_individual_transformations(combination_spec),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "parameters": json.dumps(
                        combination_spec,
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "source_file": str(source_file.relative_to(source_root)),
                    "generated_file": str(generated_file.relative_to(combination_root)),
                }
            )

        _write_metadata_csv(metadata_path, metadata_rows)

    summary = CombinedTransformationSummary(
        source_path=source_root,
        output_path=combined_root,
        combinations_found=len(enabled_combinations),
        representations_created=representations_created,
        representations_reused=representations_reused,
        metadata_paths=tuple(metadata_paths),
    )
    _print_summary(summary)
    return combined_root


def _build_transformer(combination_name: str) -> object:
    """Cria o transformador combinado solicitado."""

    combination = combination_name.lower().strip()
    transformer_class = SUPPORTED_COMBINATIONS.get(combination)
    if transformer_class is None:
        raise ValueError(f"Combinação combinada não suportada: {combination_name}")
    return transformer_class()


def _apply_transformation(
    transformer: object,
    representation: CombinedRepresentation,
    combination_name: str,
    combination_spec: dict[str, Any],
    random_seed: int,
) -> CombinedRepresentation:
    """Aplica a combinação solicitada a uma representação."""

    melody_spec = combination_spec.get("melody")
    harmony_spec = combination_spec.get("harmony")
    rhythm_spec = combination_spec.get("rhythm")

    if combination_name == "melody_harmony":
        return transformer.transform(  # type: ignore[attr-defined]
            melody=representation.melody,
            harmony=representation.harmony,
            rhythm=representation.rhythm,
            melody_transformation=melody_spec["transformation"],
            melody_parameters=dict(melody_spec.get("parameters", {})),
            harmony_transformation=harmony_spec["transformation"],
            harmony_parameters=dict(harmony_spec.get("parameters", {})),
            random_seed=random_seed,
        )
    if combination_name == "melody_rhythm":
        return transformer.transform(  # type: ignore[attr-defined]
            melody=representation.melody,
            harmony=representation.harmony,
            rhythm=representation.rhythm,
            melody_transformation=melody_spec["transformation"],
            melody_parameters=dict(melody_spec.get("parameters", {})),
            rhythm_transformation=rhythm_spec["transformation"],
            rhythm_parameters=dict(rhythm_spec.get("parameters", {})),
            random_seed=random_seed,
        )
    if combination_name == "harmony_rhythm":
        return transformer.transform(  # type: ignore[attr-defined]
            melody=representation.melody,
            harmony=representation.harmony,
            rhythm=representation.rhythm,
            harmony_transformation=harmony_spec["transformation"],
            harmony_parameters=dict(harmony_spec.get("parameters", {})),
            rhythm_transformation=rhythm_spec["transformation"],
            rhythm_parameters=dict(rhythm_spec.get("parameters", {})),
            random_seed=random_seed,
        )
    if combination_name == "melody_harmony_rhythm":
        return transformer.transform(  # type: ignore[attr-defined]
            melody=representation.melody,
            harmony=representation.harmony,
            rhythm=representation.rhythm,
            melody_transformation=melody_spec["transformation"],
            melody_parameters=dict(melody_spec.get("parameters", {})),
            harmony_transformation=harmony_spec["transformation"],
            harmony_parameters=dict(harmony_spec.get("parameters", {})),
            rhythm_transformation=rhythm_spec["transformation"],
            rhythm_parameters=dict(rhythm_spec.get("parameters", {})),
            random_seed=random_seed,
        )
    raise ValueError(f"Combinação combinada não suportada: {combination_name}")


def _get_enabled_combinations(transformation_section: dict[str, Any]) -> list[str]:
    """Retorna as combinações habilitadas na configuração."""

    enabled = transformation_section.get("enabled")
    if enabled is None:
        combinations = [
            key
            for key in transformation_section
            if key not in {"random_seed", "enabled"}
        ]
    else:
        combinations = list(enabled)

    invalid_combinations = [
        combination
        for combination in combinations
        if combination not in SUPPORTED_COMBINATIONS
    ]
    if invalid_combinations:
        raise ValueError(
            "Combinações combinadas não suportadas: "
            + ", ".join(sorted(invalid_combinations))
        )

    return combinations


def _get_combination_spec(
    transformation_section: dict[str, Any],
    combination_name: str,
) -> dict[str, Any]:
    """Obtém a especificação de uma combinação."""

    combination_spec = transformation_section.get(combination_name)
    if not isinstance(combination_spec, dict):
        raise ValueError(f"Configuração inválida para a combinação: {combination_name}")
    return combination_spec


def _build_individual_transformations(combination_spec: dict[str, Any]) -> dict[str, str]:
    """Extrai apenas os nomes das transformações individuais."""

    return {
        category: spec["transformation"]
        for category, spec in combination_spec.items()
        if isinstance(spec, dict) and "transformation" in spec
    }


def _parse_segment_identifier(segment_file: str) -> tuple[str, str]:
    """Separa o identificador da música e do segmento."""

    stem = Path(segment_file).stem
    match = re.match(r"^(?P<song_id>.+)_segment_(?P<segment_id>\d+)$", stem)
    if match is None:
        return stem, stem
    return match.group("song_id"), match.group("segment_id")


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
                "combination",
                "individual_transformations",
                "parameters",
                "source_file",
                "generated_file",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def _print_summary(summary: CombinedTransformationSummary) -> None:
    """Exibe um resumo amigável da transformação combinada."""

    print("Transformações combinadas concluídas.")
    print(f"Origem: {summary.source_path.as_posix()}")
    print(f"Saída: {summary.output_path.as_posix()}")
    print(f"Combinações habilitadas: {summary.combinations_found}")
    print(f"Representações criadas: {summary.representations_created}")
    print(f"Representações reutilizadas: {summary.representations_reused}")
    for metadata_path in summary.metadata_paths:
        print(f"Metadados gerados em: {metadata_path.as_posix()}")
