"""Pipeline da etapa de selecao de subconjunto do dataset POP909."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import random
import shutil


@dataclass(frozen=True)
class SubsetSelectionSummary:
    """Representa o resultado da selecao de subconjunto."""

    source_path: Path
    output_path: Path
    available_files: int
    selected_files: int
    random_seed: int


def select_subset(
    source_path: str | Path,
    output_path: str | Path,
    sample_size: int,
    random_seed: int,
) -> Path:
    """Seleciona aleatoriamente um subconjunto de arquivos MIDI processados.

    Args:
        source_path: Caminho da pasta `data/processed/POP909`.
        output_path: Caminho da pasta de saida `data/processed/subset`.
        sample_size: Quantidade de arquivos a serem sorteados.
        random_seed: Seed usada para garantir reprodutibilidade.

    Returns:
        O caminho da pasta de saida com o subconjunto selecionado.

    Raises:
        FileNotFoundError: Se a pasta de origem nao existir.
        ValueError: Se a quantidade solicitada for maior que a quantidade disponivel.
    """

    source_root = Path(source_path)
    subset_root = Path(output_path)

    if not source_root.is_dir():
        raise FileNotFoundError(f"Diretorio de origem nao encontrado: {source_root}")

    source_files = sorted(
        path for path in source_root.iterdir() if path.is_file() and path.suffix == ".mid"
    )

    if sample_size > len(source_files):
        raise ValueError(
            "A quantidade solicitada de arquivos excede o total disponivel no dataset."
        )

    if subset_root.exists():
        shutil.rmtree(subset_root)

    subset_root.mkdir(parents=True, exist_ok=True)

    random_generator = random.Random(random_seed)
    selected_files = sorted(
        random_generator.sample(source_files, sample_size),
        key=lambda path: path.name,
    )

    print("Iniciando a selecao do subconjunto do dataset POP909...")

    for source_file in selected_files:
        shutil.copy2(source_file, subset_root / source_file.name)

    summary = SubsetSelectionSummary(
        source_path=source_root,
        output_path=subset_root,
        available_files=len(source_files),
        selected_files=len(selected_files),
        random_seed=random_seed,
    )

    _print_subset_summary(summary)
    return subset_root


def _print_subset_summary(summary: SubsetSelectionSummary) -> None:
    """Exibe um resumo amigavel da selecao de subconjunto."""

    print("Selecao de subconjunto concluida.")
    print(f"Origem: {summary.source_path.as_posix()}")
    print(f"Saida: {summary.output_path.as_posix()}")
    print(f"Arquivos disponiveis: {summary.available_files}")
    print(f"Arquivos selecionados: {summary.selected_files}")
    print(f"Seed utilizada: {summary.random_seed}")
