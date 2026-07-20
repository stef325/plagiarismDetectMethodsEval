"""Pipeline da etapa de limpeza do dataset POP909."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import shutil
import time

from preprocessing.dataset.pop909_inspector import POP909Inspector


@dataclass(frozen=True)
class CleanSummary:
    """Representa o resultado consolidado da limpeza do dataset."""

    inspection_date: datetime
    execution_time_seconds: float
    songs_found: int
    main_midis_copied: int
    missing_main_midis: list[Path]
    output_path: Path


def clean_dataset(dataset_path: str | Path, output_path: str | Path) -> Path:
    """Copia apenas os arquivos MIDI principais do POP909 para a area processada.

    Args:
        dataset_path: Caminho do diretorio raiz do dataset bruto.
        output_path: Caminho do diretorio base de saida em `data/processed`.

    Returns:
        O caminho do diretorio processado `POP909`.

    Raises:
        FileNotFoundError: Se o dataset informado nao existir.
    """

    dataset_root = Path(dataset_path)
    processed_root = Path(output_path)
    inspection_date = datetime.now()
    start_time = time.perf_counter()

    inspector = POP909Inspector(dataset_root)
    if not inspector.dataset_exists():
        raise FileNotFoundError(f"Dataset nao encontrado: {dataset_root}")

    song_directories = inspector.list_music_directories()
    cleaned_dataset_root = processed_root / dataset_root.name

    if cleaned_dataset_root.exists():
        shutil.rmtree(cleaned_dataset_root)

    cleaned_dataset_root.mkdir(parents=True, exist_ok=True)

    main_midis_copied = 0
    missing_main_midis: list[Path] = []

    print("Iniciando a limpeza do dataset POP909...")

    for song_directory in song_directories:
        song_id = song_directory.name
        source_main_midi = song_directory / f"{song_id}.mid"

        if not source_main_midi.is_file():
            missing_main_midis.append(source_main_midi.relative_to(dataset_root))
            continue

        target_midi_path = cleaned_dataset_root / source_main_midi.name
        shutil.copy2(source_main_midi, target_midi_path)
        main_midis_copied += 1

    execution_time_seconds = time.perf_counter() - start_time
    summary = CleanSummary(
        inspection_date=inspection_date,
        execution_time_seconds=execution_time_seconds,
        songs_found=len(song_directories),
        main_midis_copied=main_midis_copied,
        missing_main_midis=missing_main_midis,
        output_path=cleaned_dataset_root,
    )

    _print_clean_summary(summary)
    return cleaned_dataset_root


def _print_clean_summary(summary: CleanSummary) -> None:
    """Exibe um resumo amigavel da limpeza do dataset."""

    print("Limpeza concluida.")
    print(f"Data da limpeza: {summary.inspection_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Musicas encontradas: {summary.songs_found}")
    print(f"Midis principais copiados: {summary.main_midis_copied}")
    print(f"Midis principais ausentes: {len(summary.missing_main_midis)}")
    print(f"Tempo de execucao: {summary.execution_time_seconds:.3f} segundos")
    print(f"Diretorio processado gerado em: {summary.output_path.as_posix()}")
