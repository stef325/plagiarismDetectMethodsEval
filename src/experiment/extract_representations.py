"""Pipeline da etapa de extracao das representacoes musicais."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shutil

import pretty_midi

from preprocessing.dataset.pop909_loader import POP909Loader
from preprocessing.representation.harmony_extractor import HarmonyExtractor
from preprocessing.representation.melody_extractor import MelodyExtractor
from preprocessing.representation.rhythm_extractor import RhythmExtractor


@dataclass(frozen=True)
class RepresentationExtractionSummary:
    """Resumo da extracao das representacoes musicais."""

    source_path: Path
    output_path: Path
    segments_found: int
    representations_saved: int
    representations_skipped: int


def extract_representations(
    source_path: str | Path,
    output_path: str | Path,
) -> Path:
    """Extrai melodia, harmonia e ritmo de cada segmento processado.

    Args:
        source_path: Caminho da pasta `data/processed/segments`.
        output_path: Caminho da pasta de saida para os JSONs.

    Returns:
        O caminho da pasta de saida das representacoes.

    Raises:
        FileNotFoundError: Se a pasta de entrada nao existir.
    """

    source_root = Path(source_path)
    representations_root = Path(output_path)

    if not source_root.is_dir():
        raise FileNotFoundError(f"Diretorio de origem nao encontrado: {source_root}")

    segments_metadata = source_root / "segments_metadata.csv"
    if not segments_metadata.is_file():
        raise FileNotFoundError(
            f"Arquivo de metadados nao encontrado: {segments_metadata}"
        )

    representations_root.mkdir(parents=True, exist_ok=True)

    loader = POP909Loader(source_root)
    melody_extractor = MelodyExtractor()
    harmony_extractor = HarmonyExtractor()
    rhythm_extractor = RhythmExtractor()

    segment_files = sorted(
        path for path in source_root.iterdir() if path.is_file() and path.suffix == ".mid"
    )
    segments_found = len(segment_files)
    representations_saved = 0
    representations_skipped = 0

    print("Iniciando a extracao das representacoes musicais...")

    for segment_file in segment_files:
        json_path = representations_root / f"{segment_file.stem}.json"
        if json_path.exists():
            representations_skipped += 1
            continue

        midi = loader.load_midi_file(segment_file)
        payload = {
            "segment_file": segment_file.name,
            "melody": melody_extractor.extract(midi),
            "harmony": harmony_extractor.extract(midi),
            "rhythm": rhythm_extractor.extract(midi),
        }

        _write_json(json_path, payload)
        representations_saved += 1

    summary = RepresentationExtractionSummary(
        source_path=source_root,
        output_path=representations_root,
        segments_found=segments_found,
        representations_saved=representations_saved,
        representations_skipped=representations_skipped,
    )

    _print_summary(summary)
    return representations_root


def _write_json(json_path: Path, payload: dict[str, object]) -> None:
    """Escreve um JSON com a representacao extraida."""

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def _print_summary(summary: RepresentationExtractionSummary) -> None:
    """Exibe um resumo amigavel da extracao de representacoes."""

    print("Extracao de representacoes concluida.")
    print(f"Origem: {summary.source_path.as_posix()}")
    print(f"Saida: {summary.output_path.as_posix()}")
    print(f"Segmentos encontrados: {summary.segments_found}")
    print(f"Representacoes salvas: {summary.representations_saved}")
    print(f"Representacoes ignoradas: {summary.representations_skipped}")
