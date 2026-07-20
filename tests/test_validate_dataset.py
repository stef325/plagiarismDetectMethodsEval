from __future__ import annotations

import sys
import tempfile
import unittest
import warnings
from importlib import import_module
from pathlib import Path
from unittest.mock import patch

import pretty_midi

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

validate_dataset = import_module("experiment.03_validate_dataset").validate_dataset


def _write_midi(path: Path) -> None:
    midi = pretty_midi.PrettyMIDI(initial_tempo=120)
    instrument = pretty_midi.Instrument(program=0)
    instrument.notes.append(
        pretty_midi.Note(velocity=100, pitch=60, start=0.0, end=0.5)
    )
    midi.instruments.append(instrument)
    midi.write(str(path))


def _create_music_dir(root: Path, song_id: str) -> Path:
    music_dir = root / song_id
    music_dir.mkdir(parents=True, exist_ok=True)

    _write_midi(music_dir / f"{song_id}.mid")
    versions_dir = music_dir / "versions"
    versions_dir.mkdir(exist_ok=True)
    _write_midi(versions_dir / f"{song_id}-v1.mid")

    return music_dir


class ValidateDatasetTestCase(unittest.TestCase):
    def test_validate_dataset_raises_for_missing_dataset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset_path = Path(tmpdir) / "missing"
            report_path = Path(tmpdir) / "report.md"

            with self.assertRaises(FileNotFoundError):
                validate_dataset(dataset_path, report_path)

    def test_validate_dataset_returns_report_path_for_valid_dataset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset_root = Path(tmpdir) / "POP909"
            _create_music_dir(dataset_root, "001")
            report_path = Path(tmpdir) / "data" / "results" / "report.md"

            result = validate_dataset(dataset_root, report_path)

            self.assertEqual(result, report_path)
            self.assertTrue(report_path.exists())

    def test_validate_dataset_writes_report_with_no_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset_root = Path(tmpdir) / "POP909"
            _create_music_dir(dataset_root, "001")
            _create_music_dir(dataset_root, "002")
            report_path = Path(tmpdir) / "data" / "results" / "report.md"

            validate_dataset(dataset_root, report_path)

            content = report_path.read_text(encoding="utf-8")
            self.assertIn("# Relatorio de Validacao do Dataset POP909", content)
            self.assertIn("- Musicas analisadas: 2", content)
            self.assertIn("- Arquivos MIDI encontrados: 4", content)
            self.assertIn("- Arquivos carregados com sucesso: 4", content)
            self.assertIn("- Arquivos MIDI com aviso: 0", content)
            self.assertIn("- Arquivos invalidos: 0", content)
            self.assertIn("Nenhum arquivo com aviso foi encontrado.", content)
            self.assertIn("Nenhum arquivo invalido encontrado.", content)

    def test_validate_dataset_records_failures_with_mock(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset_root = Path(tmpdir) / "POP909"
            _create_music_dir(dataset_root, "001")
            report_path = Path(tmpdir) / "data" / "results" / "report.md"

            with patch(
                "experiment.03_validate_dataset.POP909Loader.load_music",
                side_effect=OSError("MIDI corrompido"),
            ):
                validate_dataset(dataset_root, report_path)

            content = report_path.read_text(encoding="utf-8")
            self.assertIn("- Musicas analisadas: 1", content)
            self.assertIn("- Arquivos MIDI encontrados: 2", content)
            self.assertIn("- Arquivos carregados com sucesso: 0", content)
            self.assertIn("- Arquivos MIDI com aviso: 0", content)
            self.assertIn("- Arquivos invalidos: 2", content)
            self.assertIn("- Musica: 001", content)
            self.assertIn("- Arquivo: `001/001.mid`", content)
            self.assertIn("- Tipo da excecao: OSError", content)
            self.assertIn("- Mensagem: MIDI corrompido", content)

    def test_validate_dataset_records_warning_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset_root = Path(tmpdir) / "POP909"
            _create_music_dir(dataset_root, "001")
            report_path = Path(tmpdir) / "data" / "results" / "report.md"

            original_load_music = sys.modules[
                "experiment.03_validate_dataset"
            ].POP909Loader.load_music

            def load_music_with_warning(self: object, song_id: str) -> dict:
                warnings.warn("Aviso de teste do MIDI", RuntimeWarning)
                return original_load_music(self, song_id)

            with patch(
                "experiment.03_validate_dataset.POP909Loader.load_music",
                new=load_music_with_warning,
            ):
                validate_dataset(dataset_root, report_path)

            content = report_path.read_text(encoding="utf-8")
            self.assertIn("- Arquivos carregados com sucesso: 2", content)
            self.assertIn("- Arquivos MIDI com aviso: 2", content)
            self.assertIn("- Arquivos invalidos: 0", content)
            self.assertIn("- Tipo do aviso: RuntimeWarning", content)
            self.assertIn("- Mensagem: Aviso de teste do MIDI", content)


if __name__ == "__main__":
    unittest.main()
