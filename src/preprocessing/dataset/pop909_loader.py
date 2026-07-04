"""Carrega arquivos MIDI do POP909 sem extrair caracteristicas musicais."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pretty_midi


class POP909Loader:
    """Carrega arquivos MIDI do POP909 como objetos `pretty_midi.PrettyMIDI`."""

    def __init__(self, dataset_path: str | Path) -> None:
        self.dataset_path = Path(dataset_path)

    def get_music_directory(self, song_id: str) -> Path:
        """Retorna o caminho de um diretorio de musica do POP909.

        Args:
            song_id: Identificador da musica no POP909, como "001".

        Returns:
            O caminho do diretorio solicitado.

        Raises:
            FileNotFoundError: Se o diretorio nao existir.
        """

        music_directory = self.dataset_path / song_id
        if not music_directory.is_dir():
            raise FileNotFoundError(
                f"Diretorio da musica nao encontrado: {music_directory}"
            )
        return music_directory

    def list_music_midi_files(self, song_id: str) -> List[Path]:
        """Lista todos os arquivos MIDI de um diretorio de musica."""

        music_directory = self.get_music_directory(song_id)
        return sorted(
            music_directory.rglob("*.mid"),
            key=lambda path: path.relative_to(self.dataset_path).as_posix(),
        )

    def load_music(self, song_id: str) -> Dict[Path, pretty_midi.PrettyMIDI]:
        """Carrega todos os arquivos MIDI associados a uma musica do POP909.

        Args:
            song_id: Identificador da musica no POP909, como "001".

        Returns:
            Um mapeamento entre caminhos relativos no dataset e objetos PrettyMIDI.
        """

        loaded_midis: Dict[Path, pretty_midi.PrettyMIDI] = {}

        for midi_path in self.list_music_midi_files(song_id):
            relative_path = midi_path.relative_to(self.dataset_path)
            loaded_midis[relative_path] = pretty_midi.PrettyMIDI(str(midi_path))

        return loaded_midis
