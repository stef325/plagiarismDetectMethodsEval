"""Pipeline da etapa de extracao de segmentos do dataset POP909."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import random
import shutil

import pretty_midi

from preprocessing.dataset.pop909_loader import POP909Loader


@dataclass(frozen=True)
class SegmentExtractionSummary:
    """Representa o resultado consolidado da extracao de segmentos."""

    source_path: Path
    output_path: Path
    available_files: int
    segments_per_song: int
    measures_per_segment: int
    random_seed: int
    segments_created: int


def extract_segments(
    source_path: str | Path,
    output_path: str | Path,
    measures_per_segment: int,
    segments_per_song: int,
    random_seed: int,
) -> Path:
    """Extrai segmentos aleatorios de um numero fixo de compassos por musica.

    Args:
        source_path: Caminho da pasta com os MIDIs processados selecionados.
        output_path: Caminho da pasta de saida `data/processed/segments`.
        measures_per_segment: Quantidade exata de compassos por segmento.
        segments_per_song: Quantidade de segmentos a gerar para cada musica.
        random_seed: Seed usada para reproduzir a selecao aleatoria.

    Returns:
        O caminho da pasta de segmentos gerada.

    Raises:
        FileNotFoundError: Se a pasta de origem nao existir.
        ValueError: Se nao houver compassos suficientes para a extracao.
    """

    source_root = Path(source_path)
    segments_root = Path(output_path)

    if not source_root.is_dir():
        raise FileNotFoundError(f"Diretorio de origem nao encontrado: {source_root}")
    if measures_per_segment <= 0:
        raise ValueError("A quantidade de compassos por segmento deve ser maior que zero.")
    if segments_per_song <= 0:
        raise ValueError("A quantidade de segmentos por musica deve ser maior que zero.")

    source_files = sorted(
        path
        for path in source_root.iterdir()
        if path.is_file() and path.suffix.lower() == ".mid"
    )

    if segments_root.exists():
        shutil.rmtree(segments_root)

    segments_root.mkdir(parents=True, exist_ok=True)

    loader = POP909Loader(source_root)
    segments_created = 0

    print("Iniciando a extracao de segmentos do dataset POP909...")

    for source_file in source_files:
        midi = loader.load_midi_file(source_file)
        downbeats = midi.get_downbeats()
        available_starts = _get_available_start_indices(
            downbeats,
            measures_per_segment,
        )

        if len(available_starts) < segments_per_song:
            raise ValueError(
                "A musica "
                f"{source_file.name} nao possui compassos suficientes para gerar "
                f"{segments_per_song} segmentos de {measures_per_segment} compassos."
            )

        song_seed = _build_song_seed(random_seed, source_file.stem)
        random_generator = random.Random(song_seed)
        selected_starts = sorted(
            random_generator.sample(available_starts, segments_per_song)
        )

        for segment_index, start_index in enumerate(selected_starts, start=1):
            start_time = float(downbeats[start_index])
            end_time = float(downbeats[start_index + measures_per_segment])
            segment_midi = _extract_midi_segment(midi, start_time, end_time)
            segment_path = segments_root / (
                f"{source_file.stem}_segment_{segment_index:02d}.mid"
            )
            segment_midi.write(str(segment_path))
            segments_created += 1

    summary = SegmentExtractionSummary(
        source_path=source_root,
        output_path=segments_root,
        available_files=len(source_files),
        segments_per_song=segments_per_song,
        measures_per_segment=measures_per_segment,
        random_seed=random_seed,
        segments_created=segments_created,
    )

    _print_segment_summary(summary)
    return segments_root


def _get_available_start_indices(
    downbeats: list[float] | tuple[float, ...] | object,
    measures_per_segment: int,
) -> list[int]:
    """Calcula os indices validos de inicio dos segmentos."""

    downbeat_list = list(downbeats)
    available_starts = len(downbeat_list) - measures_per_segment
    if available_starts <= 0:
        return []
    return list(range(available_starts))


def _build_song_seed(random_seed: int, song_id: str) -> int:
    """Gera uma seed deterministica por musica."""

    seed_material = f"{random_seed}:{song_id}".encode("utf-8")
    digest = hashlib.sha256(seed_material).hexdigest()
    return int(digest[:16], 16)


def _extract_midi_segment(
    midi: pretty_midi.PrettyMIDI,
    start_time: float,
    end_time: float,
) -> pretty_midi.PrettyMIDI:
    """Recorta um segmento MIDI entre dois tempos absolutos."""

    tempo = midi.estimate_tempo() if midi.instruments else 120.0
    segment_midi = pretty_midi.PrettyMIDI(initial_tempo=tempo)

    for instrument in midi.instruments:
        segment_instrument = pretty_midi.Instrument(
            program=instrument.program,
            is_drum=instrument.is_drum,
            name=instrument.name,
        )

        for note in instrument.notes:
            if note.end <= start_time or note.start >= end_time:
                continue

            clipped_start = max(note.start, start_time) - start_time
            clipped_end = min(note.end, end_time) - start_time
            if clipped_end <= clipped_start:
                continue

            segment_instrument.notes.append(
                pretty_midi.Note(
                    velocity=note.velocity,
                    pitch=note.pitch,
                    start=clipped_start,
                    end=clipped_end,
                )
            )

        if segment_instrument.notes:
            segment_midi.instruments.append(segment_instrument)

    return segment_midi


def _print_segment_summary(summary: SegmentExtractionSummary) -> None:
    """Exibe um resumo amigavel da extracao de segmentos."""

    print("Extracao de segmentos concluida.")
    print(f"Origem: {summary.source_path.as_posix()}")
    print(f"Saida: {summary.output_path.as_posix()}")
    print(f"Arquivos de origem: {summary.available_files}")
    print(f"Segmentos por musica: {summary.segments_per_song}")
    print(f"Compassos por segmento: {summary.measures_per_segment}")
    print(f"Segmentos criados: {summary.segments_created}")
    print(f"Seed utilizada: {summary.random_seed}")
