from __future__ import annotations

import csv
import shutil
import sys
import tempfile
import unittest
from importlib import import_module
from pathlib import Path

import pretty_midi


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

inspect_dataset = import_module("experiment.01_inspect_dataset").inspect_dataset
clean_dataset = import_module("experiment.02_clean_dataset").clean_dataset
validate_dataset = import_module("experiment.03_validate_dataset").validate_dataset
POP909Inspector = import_module(
    "preprocessing.dataset.pop909_inspector"
).POP909Inspector


def _write_midi(path: Path) -> None:
    midi = pretty_midi.PrettyMIDI(initial_tempo=120)
    instrument = pretty_midi.Instrument(program=0)
    instrument.notes.append(
        pretty_midi.Note(velocity=100, pitch=60, start=0.0, end=0.5)
    )
    midi.instruments.append(instrument)
    path.parent.mkdir(parents=True, exist_ok=True)
    midi.write(str(path))


def _read_expected_output() -> dict[str, str]:
    expected_path = Path(__file__).resolve().parent / "smoke" / "expected_output.csv"
    with expected_path.open("r", encoding="utf-8", newline="") as file:
        return {row["check"]: row["expected"] for row in csv.DictReader(file)}


def _extract_summary_value(report_text: str, prefix: str) -> str:
    for line in report_text.splitlines():
        if line.startswith(prefix):
            return line.replace(prefix, "", 1).strip()
    raise AssertionError(f"Prefixo nao encontrado no relatorio: {prefix}")


class SmokeDatasetExampleTestCase(unittest.TestCase):
    """Executa um smoke test com dataset minimo e saida esperada."""

    def test_minimal_dataset_matches_expected_output(self) -> None:
        smoke_root = Path(__file__).resolve().parent / "smoke"
        expected_output = _read_expected_output()

        with tempfile.TemporaryDirectory() as temp_directory:
            temp_root = Path(temp_directory)
            dataset_source = smoke_root / "example_dataset" / "POP909"
            dataset_root = temp_root / "data" / "raw" / "POP909"
            shutil.copytree(dataset_source, dataset_root)

            _write_midi(dataset_root / "001" / "001.mid")
            _write_midi(dataset_root / "001" / "versions" / "001-v1.mid")

            inspector = POP909Inspector(dataset_root)

            inspect_report_path = temp_root / "results" / "inspect_report.md"
            clean_output_root = temp_root / "data" / "processed"
            validation_report_path = temp_root / "results" / "validation_report.md"

            inspect_dataset(dataset_root, inspect_report_path)
            cleaned_dataset_root = clean_dataset(dataset_root, clean_output_root)
            validate_dataset(dataset_root, validation_report_path)

            validation_report_text = validation_report_path.read_text(
                encoding="utf-8"
            )

            actual_output = {
                "dataset_exists": str(inspector.dataset_exists()),
                "music_count": str(inspector.count_music()),
                "invalid_directories_count": str(len(inspector.validate_structure())),
                "inspect_report_exists": str(inspect_report_path.exists()),
                "cleaned_dataset_exists": str(cleaned_dataset_root.exists()),
                "cleaned_main_midis": str(
                    len(list(cleaned_dataset_root.glob("*.mid")))
                ),
                "cleaned_contains_001_mid": str(
                    (cleaned_dataset_root / "001.mid").exists()
                ),
                "validation_report_exists": str(validation_report_path.exists()),
                "validation_songs_analyzed": _extract_summary_value(
                    validation_report_text, "- Musicas analisadas:"
                ),
                "validation_midi_files_found": _extract_summary_value(
                    validation_report_text, "- Arquivos MIDI encontrados:"
                ),
                "validation_midi_files_loaded": _extract_summary_value(
                    validation_report_text, "- Arquivos carregados com sucesso:"
                ),
                "validation_midi_files_with_warning": _extract_summary_value(
                    validation_report_text, "- Arquivos MIDI com aviso:"
                ),
                "validation_invalid_files": _extract_summary_value(
                    validation_report_text, "- Arquivos invalidos:"
                ),
            }

            assert actual_output == expected_output
