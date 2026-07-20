"""Pipeline da etapa de validacao dos arquivos MIDI do dataset."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import shutil
import tempfile
import time
import warnings

from preprocessing.dataset.pop909_inspector import POP909Inspector
from preprocessing.dataset.pop909_loader import POP909Loader


@dataclass(frozen=True)
class ValidationFailure:
    """Representa uma falha ao carregar um arquivo MIDI."""

    song_id: str
    file_path: Path
    exception_type: str
    message: str


@dataclass(frozen=True)
class ValidationWarning:
    """Representa um aviso emitido durante o carregamento de um arquivo MIDI."""

    song_id: str
    file_path: Path
    warning_type: str
    message: str


@dataclass(frozen=True)
class ValidationSummary:
    """Representa o resultado consolidado da validacao do dataset."""

    inspection_date: datetime
    execution_time_seconds: float
    songs_analyzed: int
    midi_files_found: int
    midi_files_loaded: int
    midi_files_with_warning: int
    failures: list[ValidationFailure]
    warnings: list[ValidationWarning]


def validate_dataset(dataset_path: str | Path, output_path: str | Path) -> Path:
    """Valida se os arquivos MIDI do POP909 podem ser carregados.

    Args:
        dataset_path: Caminho do diretorio raiz do dataset.
        output_path: Caminho do relatorio Markdown de saida.

    Returns:
        O caminho do relatorio gerado.

    Raises:
        FileNotFoundError: Se o dataset informado nao existir.
    """

    dataset_root = Path(dataset_path)
    report_path = Path(output_path)
    inspection_date = datetime.now()
    start_time = time.perf_counter()

    inspector = POP909Inspector(dataset_root)
    if not inspector.dataset_exists():
        raise FileNotFoundError(f"Dataset nao encontrado: {dataset_root}")

    song_directories = inspector.list_music_directories()
    loader = POP909Loader(dataset_root)
    midi_files_found = 0
    midi_files_loaded = 0
    failures: list[ValidationFailure] = []
    warning_entries: list[ValidationWarning] = []

    print("Iniciando a validacao dos arquivos MIDI do dataset POP909...")

    for song_directory in song_directories:
        song_id = song_directory.name
        midi_files = loader.list_music_midi_files(song_id)
        midi_files_found += len(midi_files)
        (
            song_loaded_count,
            song_warning_entries,
            song_failures,
        ) = _validate_song_files_individually(
            dataset_root=dataset_root,
            song_id=song_id,
            midi_files=midi_files,
        )
        midi_files_loaded += song_loaded_count
        warning_entries.extend(song_warning_entries)
        failures.extend(song_failures)

    execution_time_seconds = time.perf_counter() - start_time
    summary = ValidationSummary(
        inspection_date=inspection_date,
        execution_time_seconds=execution_time_seconds,
        songs_analyzed=len(song_directories),
        midi_files_found=midi_files_found,
        midi_files_loaded=midi_files_loaded,
        midi_files_with_warning=len(warning_entries),
        failures=failures,
        warnings=warning_entries,
    )

    _write_validation_report(report_path, summary)
    _print_validation_summary(summary, report_path)

    return report_path


def _validate_song_files_individually(
    dataset_root: Path,
    song_id: str,
    midi_files: list[Path],
) -> tuple[int, list[ValidationWarning], list[ValidationFailure]]:
    """Valida individualmente os arquivos MIDI de uma musica."""

    midi_files_loaded = 0
    warning_entries: list[ValidationWarning] = []
    failures: list[ValidationFailure] = []

    for midi_file in midi_files:
        try:
            emitted_warnings = _load_single_midi_file(dataset_root, song_id, midi_file)
        except Exception as error:
            failures.append(
                ValidationFailure(
                    song_id=song_id,
                    file_path=midi_file.relative_to(dataset_root),
                    exception_type=type(error).__name__,
                    message=str(error),
                )
            )
        else:
            midi_files_loaded += 1
            warning_entries.extend(
                ValidationWarning(
                    song_id=song_id,
                    file_path=midi_file.relative_to(dataset_root),
                    warning_type=type(warning_message.message).__name__,
                    message=str(warning_message.message),
                )
                for warning_message in emitted_warnings
            )

    return midi_files_loaded, warning_entries, failures


def _load_single_midi_file(
    dataset_root: Path, song_id: str, midi_file: Path
) -> list[warnings.WarningMessage]:
    """Carrega um unico arquivo MIDI usando exclusivamente o POP909Loader."""

    song_root = dataset_root / song_id
    relative_file_path = midi_file.relative_to(song_root)

    with tempfile.TemporaryDirectory() as temp_directory:
        temp_root = Path(temp_directory)
        temp_song_root = temp_root / song_id
        temp_file_path = temp_song_root / relative_file_path

        temp_file_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(midi_file, temp_file_path)

        isolated_loader = POP909Loader(temp_root)
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            isolated_loader.load_music(song_id)

        return caught_warnings


def _write_validation_report(report_path: Path, summary: ValidationSummary) -> None:
    """Escreve o relatorio Markdown da validacao."""

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        "\n".join(_build_report_lines(summary)) + "\n",
        encoding="utf-8",
    )


def _build_report_lines(summary: ValidationSummary) -> list[str]:
    """Monta as linhas do relatorio Markdown."""

    lines = [
        "# Relatorio de Validacao do Dataset POP909",
        "",
        f"Data: {summary.inspection_date.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"Tempo de execucao: {summary.execution_time_seconds:.3f} segundos",
        "",
        "## Resumo",
        "",
        f"- Musicas analisadas: {summary.songs_analyzed}",
        f"- Arquivos MIDI encontrados: {summary.midi_files_found}",
        f"- Arquivos carregados com sucesso: {summary.midi_files_loaded}",
        f"- Arquivos MIDI com aviso: {summary.midi_files_with_warning}",
        f"- Arquivos invalidos: {len(summary.failures)}",
        "",
        "## Arquivos com aviso",
        "",
    ]

    if not summary.warnings:
        lines.append("Nenhum arquivo com aviso foi encontrado.")
    else:
        for warning_entry in summary.warnings:
            lines.append(f"- Musica: {warning_entry.song_id}")
            lines.append(f"- Arquivo: `{warning_entry.file_path.as_posix()}`")
            lines.append(f"- Tipo do aviso: {warning_entry.warning_type}")
            lines.append(f"- Mensagem: {warning_entry.message}")
            lines.append("")

    lines.extend(
        [
        "## Arquivos com erro",
        "",
        ]
    )

    if not summary.failures:
        lines.append("Nenhum arquivo invalido encontrado.")
        return lines

    for failure in summary.failures:
        lines.append(f"- Musica: {failure.song_id}")
        lines.append(f"- Arquivo: `{failure.file_path.as_posix()}`")
        lines.append(f"- Tipo da excecao: {failure.exception_type}")
        lines.append(f"- Mensagem: {failure.message}")
        lines.append("")

    return lines


def _print_validation_summary(summary: ValidationSummary, report_path: Path) -> None:
    """Exibe um resumo da validacao ao usuario."""

    print("Validacao concluida.")
    print(f"Musicas analisadas: {summary.songs_analyzed}")
    print(f"Arquivos MIDI encontrados: {summary.midi_files_found}")
    print(f"Arquivos carregados com sucesso: {summary.midi_files_loaded}")
    print(f"Arquivos MIDI com aviso: {summary.midi_files_with_warning}")
    print(f"Arquivos invalidos: {len(summary.failures)}")
    print(f"Tempo de execucao: {summary.execution_time_seconds:.3f} segundos")
    print(f"Relatorio gerado em: {report_path.as_posix()}")
