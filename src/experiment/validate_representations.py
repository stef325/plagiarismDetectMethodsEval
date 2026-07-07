"""Pipeline de validacao das representacoes musicais extraidas."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import csv
import json
from pathlib import Path
import time


@dataclass(frozen=True)
class RepresentationValidationFailure:
    """Representa uma inconsistência encontrada em um segmento."""

    segment_file: str
    issue_type: str
    message: str


@dataclass(frozen=True)
class RepresentationValidationSummary:
    """Representa o resultado consolidado da validacao."""

    inspection_date: datetime
    execution_time_seconds: float
    representations_extracted: int
    valid_melodies: int
    valid_harmonies: int
    valid_rhythms: int
    failures: list[RepresentationValidationFailure]


def validate_representations(
    representations_path: str | Path,
    segments_metadata_path: str | Path,
    output_path: str | Path,
) -> Path:
    """Valida as representacoes musicais extraidas para cada segmento.

    Args:
        representations_path: Caminho da pasta com os JSONs das representacoes.
        segments_metadata_path: Caminho do CSV com os metadados dos segmentos.
        output_path: Caminho do relatorio Markdown de saida.

    Returns:
        O caminho do relatorio gerado.

    Raises:
        FileNotFoundError: Se a pasta de representacoes ou o CSV nao existirem.
    """

    representations_root = Path(representations_path)
    metadata_csv = Path(segments_metadata_path)
    report_path = Path(output_path)
    inspection_date = datetime.now()
    start_time = time.perf_counter()

    if not representations_root.is_dir():
        raise FileNotFoundError(
            f"Diretorio de representacoes nao encontrado: {representations_root}"
        )
    if not metadata_csv.is_file():
        raise FileNotFoundError(f"Arquivo de metadados nao encontrado: {metadata_csv}")

    segment_metadata = _load_segment_metadata(metadata_csv)
    validation_failures: list[RepresentationValidationFailure] = []
    valid_melodies = 0
    valid_harmonies = 0
    valid_rhythms = 0

    print("Iniciando a validacao das representacoes extraidas...")

    for segment_file, metadata in segment_metadata.items():
        json_path = representations_root / f"{Path(segment_file).stem}.json"

        if not json_path.is_file():
            validation_failures.append(
                RepresentationValidationFailure(
                    segment_file=segment_file,
                    issue_type="ArquivoAusente",
                    message="O arquivo JSON da representacao nao foi encontrado.",
                )
            )
            continue

        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            validation_failures.append(
                RepresentationValidationFailure(
                    segment_file=segment_file,
                    issue_type="JsonInvalido",
                    message=str(error),
                )
            )
            continue

        segment_failures = _validate_segment_payload(
            segment_file=segment_file,
            payload=payload,
            metadata=metadata,
        )
        validation_failures.extend(segment_failures)

        melody = payload.get("melody", [])
        harmony = payload.get("harmony", [])
        rhythm = payload.get("rhythm", [])

        if isinstance(melody, list) and melody and not any(
            failure.issue_type == "MelodiaVazia" for failure in segment_failures
        ):
            valid_melodies += 1
        if isinstance(harmony, list) and harmony and not any(
            failure.issue_type == "HarmoniaVazia" for failure in segment_failures
        ):
            valid_harmonies += 1
        if isinstance(rhythm, list) and rhythm and not any(
            failure.issue_type == "RitmoVazio" for failure in segment_failures
        ):
            valid_rhythms += 1

    for unexpected_json in _find_unexpected_json_files(representations_root, segment_metadata):
        validation_failures.append(
            RepresentationValidationFailure(
                segment_file=unexpected_json.name,
                issue_type="ArquivoInesperado",
                message="O JSON nao corresponde a nenhum segmento conhecido.",
            )
        )

    execution_time_seconds = time.perf_counter() - start_time
    summary = RepresentationValidationSummary(
        inspection_date=inspection_date,
        execution_time_seconds=execution_time_seconds,
        representations_extracted=len(segment_metadata),
        valid_melodies=valid_melodies,
        valid_harmonies=valid_harmonies,
        valid_rhythms=valid_rhythms,
        failures=validation_failures,
    )

    _write_validation_report(report_path, summary)
    _print_validation_summary(summary, report_path)
    return report_path


def _load_segment_metadata(metadata_csv: Path) -> dict[str, dict[str, str]]:
    """Carrega os metadados dos segmentos em um dicionario."""

    segment_metadata: dict[str, dict[str, str]] = {}

    with metadata_csv.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            segment_file = row["segment_file"]
            segment_metadata[segment_file] = row

    return segment_metadata


def _validate_segment_payload(
    segment_file: str,
    payload: dict[str, object],
    metadata: dict[str, str],
) -> list[RepresentationValidationFailure]:
    """Valida o conteúdo de um JSON de representacoes."""

    failures: list[RepresentationValidationFailure] = []
    expected_segment_name = segment_file

    if payload.get("segment_file") != expected_segment_name:
        failures.append(
            RepresentationValidationFailure(
                segment_file=segment_file,
                issue_type="SegmentoInconsistente",
                message="O nome do segmento no JSON nao corresponde ao metadado.",
            )
        )

    measures = _parse_integer(metadata.get("measures", "0"))
    if measures <= 0:
        failures.append(
            RepresentationValidationFailure(
                segment_file=segment_file,
                issue_type="MedidasInvalidas",
                message="A quantidade de compassos do segmento nao e valida.",
            )
        )

    melody = payload.get("melody")
    harmony = payload.get("harmony")
    rhythm = payload.get("rhythm")

    if not isinstance(melody, list):
        failures.append(
            RepresentationValidationFailure(
                segment_file=segment_file,
                issue_type="MelodiaInvalida",
                message="A melodia nao foi salva como lista.",
            )
        )
    elif not melody:
        failures.append(
            RepresentationValidationFailure(
                segment_file=segment_file,
                issue_type="MelodiaVazia",
                message="A melodia extraida esta vazia.",
            )
        )

    if not isinstance(harmony, list):
        failures.append(
            RepresentationValidationFailure(
                segment_file=segment_file,
                issue_type="HarmoniaInvalida",
                message="A harmonia nao foi salva como lista.",
            )
        )
    elif not harmony:
        failures.append(
            RepresentationValidationFailure(
                segment_file=segment_file,
                issue_type="HarmoniaVazia",
                message="A harmonia extraida esta vazia.",
            )
        )

    if not isinstance(rhythm, list):
        failures.append(
            RepresentationValidationFailure(
                segment_file=segment_file,
                issue_type="RitmoInvalido",
                message="O ritmo nao foi salvo como lista.",
            )
        )
    elif not rhythm:
        failures.append(
            RepresentationValidationFailure(
                segment_file=segment_file,
                issue_type="RitmoVazio",
                message="O ritmo extraido esta vazio.",
            )
        )

    if isinstance(melody, list) and isinstance(rhythm, list) and melody and rhythm:
        if len(melody) > len(rhythm):
            failures.append(
                RepresentationValidationFailure(
                    segment_file=segment_file,
                    issue_type="TamanhoIncoerente",
                    message="A melodia possui mais eventos do que o ritmo.",
                )
            )

    if isinstance(harmony, list) and isinstance(rhythm, list) and harmony and rhythm:
        if len(harmony) > len(rhythm):
            failures.append(
                RepresentationValidationFailure(
                    segment_file=segment_file,
                    issue_type="TamanhoIncoerente",
                    message="A harmonia possui mais eventos do que o ritmo.",
                )
            )

    return failures


def _parse_integer(value: object) -> int:
    """Converte um valor para inteiro de forma segura."""

    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _find_unexpected_json_files(
    representations_root: Path,
    segment_metadata: dict[str, dict[str, str]],
) -> list[Path]:
    """Identifica JSONs que nao correspondem a segmentos conhecidos."""

    expected_json_names = {f"{Path(segment_file).stem}.json" for segment_file in segment_metadata}
    return sorted(
        path
        for path in representations_root.iterdir()
        if path.is_file()
        and path.suffix.lower() == ".json"
        and path.name not in expected_json_names
    )


def _write_validation_report(
    report_path: Path,
    summary: RepresentationValidationSummary,
) -> None:
    """Escreve o relatorio Markdown da validacao."""

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        "\n".join(_build_report_lines(summary)) + "\n",
        encoding="utf-8",
    )


def _build_report_lines(summary: RepresentationValidationSummary) -> list[str]:
    """Monta as linhas do relatorio Markdown."""

    lines = [
        "# Relatorio de Validacao das Representacoes do Dataset POP909",
        "",
        f"Data: {summary.inspection_date.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"Tempo de execucao: {summary.execution_time_seconds:.3f} segundos",
        "",
        "## Resumo",
        "",
        f"- Representacoes extraidas: {summary.representations_extracted}",
        f"- Melodias validas: {summary.valid_melodies}",
        f"- Harmonias validas: {summary.valid_harmonies}",
        f"- Ritmos validos: {summary.valid_rhythms}",
        f"- Falhas: {len(summary.failures)}",
        "",
        "## Falhas",
        "",
    ]

    if not summary.failures:
        lines.append("Nenhuma falha encontrada.")
        return lines

    for failure in summary.failures:
        lines.append(f"- Segmento: {failure.segment_file}")
        lines.append(f"- Tipo: {failure.issue_type}")
        lines.append(f"- Mensagem: {failure.message}")
        lines.append("")

    return lines


def _print_validation_summary(
    summary: RepresentationValidationSummary,
    report_path: Path,
) -> None:
    """Exibe um resumo amigavel da validacao."""

    print("Validacao das representacoes concluida.")
    print(f"Representacoes extraidas: {summary.representations_extracted}")
    print(f"Melodias validas: {summary.valid_melodies}")
    print(f"Harmonias validas: {summary.valid_harmonies}")
    print(f"Ritmos validos: {summary.valid_rhythms}")
    print(f"Falhas: {len(summary.failures)}")
    print(f"Tempo de execucao: {summary.execution_time_seconds:.3f} segundos")
    print(f"Relatorio gerado em: {report_path.as_posix()}")
