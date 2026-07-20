"""Pipeline para validacao das transformacoes geradas pelo experimento."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import csv
import json
from pathlib import Path
import time
from typing import Any

from validation.combined_validator import CombinedValidator
from validation.harmony_validator import HarmonyValidator
from validation.melody_validator import MelodyValidator
from validation.rhythm_validator import RhythmValidator
from validation._helpers import (
    load_combined_representation,
    load_harmony_representation,
    load_melody_representation,
    load_rhythm_representation,
)
from validation._models import ValidationResult


@dataclass(frozen=True)
class TransformationValidationSummary:
    """Resumo consolidado da validacao das transformacoes."""

    source_path: Path
    representations_path: Path
    output_path: Path
    inspection_date: datetime
    execution_time_seconds: float
    metadata_files_found: int
    validations_run: int
    validations_reused: int
    validations_passed: int
    validations_failed: int


def validate_transformations(
    transformations_path: str | Path,
    representations_path: str | Path,
    output_path: str | Path,
) -> Path:
    """Valida todas as transformacoes existentes sem recalcular os dados.

    Args:
        transformations_path: Pasta raiz com as transformacoes geradas.
        representations_path: Pasta com as representacoes originais.
        output_path: Pasta de saida dos relatorios de validacao.

    Returns:
        O caminho da pasta de validacao.

    Raises:
        FileNotFoundError: Se alguma pasta obrigatoria nao existir.
        ValueError: Se nao houver transformacoes para validar.
    """

    source_root = Path(transformations_path)
    representations_root = Path(representations_path)
    validation_root = Path(output_path)
    inspection_date = datetime.now()
    start_time = time.perf_counter()

    if not source_root.is_dir():
        raise FileNotFoundError(f"Diretorio de transformacoes nao encontrado: {source_root}")
    if not representations_root.is_dir():
        raise FileNotFoundError(
            f"Diretorio de representacoes nao encontrado: {representations_root}"
        )

    metadata_files = _find_metadata_files(source_root)
    if not metadata_files:
        raise ValueError("Nao ha transformacoes para validar.")

    print("Iniciando a validacao das transformacoes...")

    all_results: list[ValidationResult] = []
    validations_reused = 0

    for metadata_path in metadata_files:
        validation_csv_path = _build_validation_cache_path(
            validation_root=validation_root,
            source_root=source_root,
            metadata_path=metadata_path,
        )
        if validation_csv_path.is_file():
            all_results.extend(_read_validation_results(validation_csv_path))
            validations_reused += 1
            continue

        results = _validate_metadata_file(
            metadata_path=metadata_path,
            representations_root=representations_root,
            validation_csv_path=validation_csv_path,
        )
        all_results.extend(results)

    summary = TransformationValidationSummary(
        source_path=source_root,
        representations_path=representations_root,
        output_path=validation_root,
        inspection_date=inspection_date,
        execution_time_seconds=time.perf_counter() - start_time,
        metadata_files_found=len(metadata_files),
        validations_run=len(metadata_files) - validations_reused,
        validations_reused=validations_reused,
        validations_passed=sum(1 for result in all_results if result.status == "PASS"),
        validations_failed=sum(1 for result in all_results if result.status == "FAIL"),
    )

    validation_root.mkdir(parents=True, exist_ok=True)
    report_path = validation_root / "transformations_validation_report.md"
    _write_markdown_report(report_path, summary, all_results)
    _print_summary(summary, report_path)
    return validation_root


def _find_metadata_files(source_root: Path) -> list[Path]:
    """Localiza os arquivos de metadados das transformacoes."""

    return sorted(
        path
        for path in source_root.rglob("metadata.csv")
        if "validation" not in path.parts
    )


def _validate_metadata_file(
    metadata_path: Path,
    representations_root: Path,
    validation_csv_path: Path,
) -> list[ValidationResult]:
    """Valida um unico arquivo de metadados de transformacao."""

    metadata_rows = _load_metadata_rows(metadata_path)
    category = metadata_path.parents[2].name
    validator = _build_validator(category)
    validation_results: list[ValidationResult] = []

    validation_csv_path.parent.mkdir(parents=True, exist_ok=True)

    for row in metadata_rows:
        result = _validate_row(
            row=row,
            category=category,
            validator=validator,
            metadata_path=metadata_path,
            representations_root=representations_root,
        )
        validation_results.append(result)

    _write_validation_csv(validation_csv_path, validation_results)
    return validation_results


def _validate_row(
    row: dict[str, str],
    category: str,
    validator: object,
    metadata_path: Path,
    representations_root: Path,
) -> ValidationResult:
    """Valida uma linha do CSV de metadados."""

    source_file = representations_root / row["source_file"]
    transformed_file = metadata_path.parent / row["generated_file"]
    song_id = row.get("song_id", "")
    segment_id = row.get("segment_id", "")
    parameters = _load_json_field(row.get("parameters", "{}"))

    try:
        original = load_combined_representation(source_file)
        transformed = _load_transformed_representation(category, transformed_file)
        metadata = _build_metadata_payload(category, row, parameters)
        if category == "melody":
            return validator.validate(  # type: ignore[attr-defined]
                original,
                transformed,
                metadata,
            )
        if category == "harmony":
            return validator.validate(  # type: ignore[attr-defined]
                original,
                transformed,
                metadata,
            )
        if category == "rhythm":
            return validator.validate(  # type: ignore[attr-defined]
                original,
                transformed,
                metadata,
            )
        if category == "combined":
            return validator.validate(  # type: ignore[attr-defined]
                original,
                transformed,
                metadata,
            )
        raise ValueError(f"Categoria de transformacao desconhecida: {category}")
    except Exception as error:
        return ValidationResult(
            song_id=song_id,
            segment_id=segment_id,
            transformation_type=row.get("transformation", row.get("combination", "")),
            expected_changed_components=_expected_changed_components(category, row),
            preserved_components=_preserved_components(category, row),
            parameters=parameters if isinstance(parameters, dict) else {},
            status="FAIL",
            error_message=str(error),
        )


def _build_validator(category: str) -> object:
    """Cria o validador adequado para a categoria informada."""

    if category == "melody":
        return MelodyValidator()
    if category == "harmony":
        return HarmonyValidator()
    if category == "rhythm":
        return RhythmValidator()
    if category == "combined":
        return CombinedValidator()
    raise ValueError(f"Categoria de transformacao desconhecida: {category}")


def _load_transformed_representation(category: str, transformed_file: Path) -> object:
    """Carrega a representacao transformada conforme a categoria."""

    if category == "melody":
        return load_melody_representation(transformed_file)
    if category == "harmony":
        return load_harmony_representation(transformed_file)
    if category == "rhythm":
        return load_rhythm_representation(transformed_file)
    if category == "combined":
        return load_combined_representation(transformed_file)
    raise ValueError(f"Categoria de transformacao desconhecida: {category}")


def _build_metadata_payload(
    category: str,
    row: dict[str, str],
    parameters: dict[str, Any],
) -> dict[str, Any]:
    """Normaliza os metadados para o validador correspondente."""

    if category == "combined":
        return {
            "combination": row.get("combination", ""),
            "parameters": parameters,
            "individual_transformations": _load_json_field(
                row.get("individual_transformations", "{}")
            ),
        }

    return {
        "transformation": row.get("transformation", ""),
        "parameters": parameters,
    }


def _expected_changed_components(category: str, row: dict[str, str]) -> tuple[str, ...]:
    """Retorna os componentes esperados como alterados."""

    if category == "combined":
        combination = row.get("combination", "")
        return tuple(_load_combination_components(combination))
    return (category,)


def _preserved_components(category: str, row: dict[str, str]) -> tuple[str, ...]:
    """Retorna os componentes esperados como preservados."""

    all_components = ("melody", "harmony", "rhythm")
    changed_components = set(_expected_changed_components(category, row))
    return tuple(component for component in all_components if component not in changed_components)


def _load_combination_components(combination: str) -> tuple[str, ...]:
    """Carrega os componentes de uma combinacao conhecida."""

    combinations = {
        "melody_harmony": ("melody", "harmony"),
        "melody_rhythm": ("melody", "rhythm"),
        "harmony_rhythm": ("harmony", "rhythm"),
        "melody_harmony_rhythm": ("melody", "harmony", "rhythm"),
    }
    return combinations.get(combination, ())


def _load_metadata_rows(metadata_path: Path) -> list[dict[str, str]]:
    """Carrega as linhas do CSV de metadados."""

    with metadata_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def _build_validation_cache_path(
    validation_root: Path,
    source_root: Path,
    metadata_path: Path,
) -> Path:
    """Constrói o caminho do cache de validacao para um arquivo de metadados."""

    relative_leaf = metadata_path.parent.relative_to(source_root)
    return validation_root / relative_leaf / "validation.csv"


def _load_json_field(value: Any) -> dict[str, Any]:
    """Converte um valor JSON armazenado em texto para dicionario."""

    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip():
        loaded = json.loads(value)
        if isinstance(loaded, dict):
            return loaded
    return {}


def _write_validation_csv(validation_csv_path: Path, results: list[ValidationResult]) -> None:
    """Escreve o CSV com os resultados da validacao."""

    with validation_csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "song_id",
                "segment_id",
                "transformation_type",
                "expected_changed_components",
                "preserved_components",
                "parameters",
                "result",
                "error_message",
            ],
        )
        writer.writeheader()
        writer.writerows(result.to_row() for result in results)


def _read_validation_results(validation_csv_path: Path) -> list[ValidationResult]:
    """Lê resultados de validacao previamente cacheados."""

    results: list[ValidationResult] = []
    with validation_csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            results.append(
                ValidationResult(
                    song_id=row.get("song_id", ""),
                    segment_id=row.get("segment_id", ""),
                    transformation_type=row.get("transformation_type", ""),
                    expected_changed_components=_split_components(
                        row.get("expected_changed_components", "")
                    ),
                    preserved_components=_split_components(row.get("preserved_components", "")),
                    parameters=_load_json_field(row.get("parameters", "{}")),
                    status=row.get("result", "PASS"),
                    error_message=row.get("error_message", ""),
                )
            )
    return results


def _split_components(value: str | None) -> tuple[str, ...]:
    """Converte uma string de componentes em tupla."""

    if not value:
        return ()
    return tuple(component.strip() for component in value.split(",") if component.strip())


def _write_markdown_report(
    report_path: Path,
    summary: TransformationValidationSummary,
    results: list[ValidationResult],
) -> None:
    """Escreve o relatorio consolidado em Markdown."""

    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Relatório de Validação das Transformações",
        "",
        f"Data: {summary.inspection_date.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"Tempo de execução: {summary.execution_time_seconds:.3f} segundos",
        "",
        "## Resumo",
        "",
        f"- Arquivos de metadados encontrados: {summary.metadata_files_found}",
        f"- Validações executadas: {summary.validations_run}",
        f"- Validações reutilizadas: {summary.validations_reused}",
        f"- Validações aprovadas: {summary.validations_passed}",
        f"- Validações reprovadas: {summary.validations_failed}",
        "",
        "## Resultados",
        "",
        "| Música | Segmento | Tipo | Componentes alterados | Componentes preservados | Parâmetros | Resultado | Erro |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for result in results:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_markdown(result.song_id),
                    _escape_markdown(result.segment_id),
                    _escape_markdown(result.transformation_type),
                    _escape_markdown(", ".join(result.expected_changed_components)),
                    _escape_markdown(", ".join(result.preserved_components)),
                    _escape_markdown(json.dumps(result.parameters, ensure_ascii=False, sort_keys=True)),
                    _escape_markdown(result.status),
                    _escape_markdown(result.error_message or "-"),
                ]
            )
            + " |"
        )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _escape_markdown(value: str) -> str:
    """Escapa caracteres especiais para tabelas Markdown."""

    return value.replace("|", "\\|").replace("\n", " ")


def _print_summary(summary: TransformationValidationSummary, report_path: Path) -> None:
    """Exibe um resumo amigável da validacao."""

    print("Validacao das transformacoes concluida.")
    print(f"Origem: {summary.source_path.as_posix()}")
    print(f"Representacoes: {summary.representations_path.as_posix()}")
    print(f"Saida: {summary.output_path.as_posix()}")
    print(f"Arquivos de metadados encontrados: {summary.metadata_files_found}")
    print(f"Validacoes executadas: {summary.validations_run}")
    print(f"Validacoes reutilizadas: {summary.validations_reused}")
    print(f"Validacoes aprovadas: {summary.validations_passed}")
    print(f"Validacoes reprovadas: {summary.validations_failed}")
    print(f"Tempo de execucao: {summary.execution_time_seconds:.3f} segundos")
    print(f"Relatorio gerado em: {report_path.as_posix()}")
