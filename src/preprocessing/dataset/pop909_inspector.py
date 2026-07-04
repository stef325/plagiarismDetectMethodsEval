"""Utilitarios para inspecionar a estrutura de diretorios do POP909."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass(frozen=True)
class DatasetSummary:
    """Resumo estruturado da arvore de diretorios do POP909."""

    dataset_path: Path
    exists: bool
    music_count: int
    valid_music_directories: int
    invalid_directories: Dict[str, List[str]]


class POP909Inspector:
    """Inspeciona a organizacao do POP909 sem ler o conteudo dos MIDIs."""

    EXPECTED_FILES: tuple[str, ...] = (
        "beat_audio.txt",
        "beat_midi.txt",
        "chord_audio.txt",
        "chord_midi.txt",
        "key_audio.txt",
    )
    EXPECTED_DIRECTORIES: tuple[str, ...] = ("versions",)
    SUMMARY_SEPARATOR = "====================================="

    def __init__(self, dataset_path: str | Path) -> None:
        self.dataset_path = Path(dataset_path)

    def dataset_exists(self) -> bool:
        """Retorna se o diretorio raiz do dataset existe."""

        return self.dataset_path.is_dir()

    def list_music_directories(self) -> List[Path]:
        """Lista os diretorios imediatos que representam musicas."""

        if not self.dataset_exists():
            return []

        return sorted(
            (
                child
                for child in self.dataset_path.iterdir()
                if child.is_dir() and child.name.isdigit()
            ),
            key=lambda path: path.name,
        )

    def get_music_directory(self, song_id: str) -> Path:
        """Retorna o caminho do diretorio de uma musica.

        Args:
            song_id: Identificador da musica no POP909, como "001".

        Returns:
            O caminho para o diretorio da musica.

        Raises:
            FileNotFoundError: Se o diretorio nao existir.
        """

        music_directory = self.dataset_path / song_id
        if not music_directory.is_dir():
            raise FileNotFoundError(
                f"Diretorio da musica nao encontrado: {music_directory}"
            )
        return music_directory

    def count_music(self) -> int:
        """Conta quantos diretorios de musica existem no dataset."""

        return len(self.list_music_directories())

    def validate_structure(self) -> Dict[str, List[str]]:
        """Verifica a estrutura esperada do POP909 em cada diretorio."""

        missing_by_directory: Dict[str, List[str]] = {}

        for music_dir in self.list_music_directories():
            missing = self._find_missing_entries(music_dir)
            if missing:
                missing_by_directory[music_dir.name] = missing

        return missing_by_directory

    def generate_summary_report(self) -> DatasetSummary:
        """Gera um resumo estruturado da arvore do dataset."""

        music_count = self.count_music()
        invalid_directories = self.validate_structure()
        valid_music_directories = music_count - len(invalid_directories)

        return DatasetSummary(
            dataset_path=self.dataset_path,
            exists=self.dataset_exists(),
            music_count=music_count,
            valid_music_directories=valid_music_directories,
            invalid_directories=invalid_directories,
        )

    def print_summary(self) -> None:
        """Exibe um resumo amigavel da inspecao do dataset."""

        summary = self.generate_summary_report()
        print(self.SUMMARY_SEPARATOR)
        print("Dataset: POP909")
        print(f"Caminho: {summary.dataset_path.as_posix()}")
        print()
        print(f"Dataset encontrado: {'Sim' if summary.exists else 'Nao'}")
        print()
        print(f"Numero de musicas: {summary.music_count}")
        print()
        print(f"Diretorios validos: {summary.valid_music_directories}")
        print()
        print(f"Diretorios invalidos: {len(summary.invalid_directories)}")
        print(self.SUMMARY_SEPARATOR)

    def export_report(self, output_path: Path) -> None:
        """Exporta o resumo da inspecao para um relatorio Markdown.

        Args:
            output_path: Caminho de destino do relatorio Markdown gerado.
        """

        summary = self.generate_summary_report()
        report_lines = self._build_report_lines(summary)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    def _find_missing_entries(self, music_dir: Path) -> List[str]:
        """Retorna os itens esperados que estao ausentes em um diretorio."""

        song_id = music_dir.name
        missing: List[str] = []

        expected_mid_file = music_dir / f"{song_id}.mid"
        if not expected_mid_file.is_file():
            missing.append(f"{song_id}.mid")

        for expected_file in self.EXPECTED_FILES:
            expected_path = music_dir / expected_file
            if not expected_path.is_file():
                missing.append(expected_file)

        for expected_directory in self.EXPECTED_DIRECTORIES:
            expected_path = music_dir / expected_directory
            if not expected_path.is_dir():
                missing.append(f"{expected_directory}/")

        return missing

    def _build_report_lines(self, summary: DatasetSummary) -> List[str]:
        """Monta as linhas do relatorio Markdown de inspecao."""

        inspection_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            "# Relatorio de Inspecao do POP909",
            "",
            f"- Data da inspecao: {inspection_date}",
            f"- Caminho do dataset: `{summary.dataset_path.as_posix()}`",
            f"- Numero de musicas: {summary.music_count}",
            f"- Numero de diretorios validos: {summary.valid_music_directories}",
            f"- Numero de diretorios invalidos: {len(summary.invalid_directories)}",
            "",
            "## Diretorios invalidos",
            "",
        ]

        if not summary.invalid_directories:
            lines.append("Nenhum diretorio invalido foi encontrado.")
            return lines

        for directory_name, missing_entries in summary.invalid_directories.items():
            lines.append(f"### {directory_name}")
            lines.append("")
            lines.append("Arquivos ou diretorios faltantes:")
            for missing_entry in missing_entries:
                lines.append(f"- `{missing_entry}`")
            lines.append("")

        return lines
