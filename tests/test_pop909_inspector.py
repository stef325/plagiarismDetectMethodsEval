from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from src.preprocessing.dataset.pop909_inspector import DatasetSummary, POP909Inspector


def _create_music_dir(
    root: Path,
    song_id: str,
    *,
    with_expected_files: bool = True,
    with_versions_dir: bool = True,
) -> Path:
    music_dir = root / song_id
    music_dir.mkdir(parents=True, exist_ok=True)

    if with_expected_files:
        (music_dir / f"{song_id}.mid").write_text("midi placeholder", encoding="utf-8")
        (music_dir / "beat_audio.txt").write_text("beat audio", encoding="utf-8")
        (music_dir / "beat_midi.txt").write_text("beat midi", encoding="utf-8")
        (music_dir / "chord_audio.txt").write_text("chord audio", encoding="utf-8")
        (music_dir / "chord_midi.txt").write_text("chord midi", encoding="utf-8")
        (music_dir / "key_audio.txt").write_text("key audio", encoding="utf-8")

    if with_versions_dir:
        versions_dir = music_dir / "versions"
        versions_dir.mkdir(exist_ok=True)
        (versions_dir / f"{song_id}-v1.mid").write_text("version midi", encoding="utf-8")

    return music_dir


class POP909InspectorTestCase(unittest.TestCase):
    def test_dataset_exists_returns_false_for_missing_directory(self) -> None:
        inspector = POP909Inspector(Path(tempfile.gettempdir()) / "missing-pop909")

        self.assertFalse(inspector.dataset_exists())

    def test_dataset_exists_returns_true_for_existing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            inspector = POP909Inspector(Path(tmpdir))

            self.assertTrue(inspector.dataset_exists())

    def test_list_music_directories_returns_sorted_numeric_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _create_music_dir(root, "010")
            _create_music_dir(root, "002")
            (root / "notes").mkdir()

            inspector = POP909Inspector(root)
            result = inspector.list_music_directories()

            self.assertEqual([path.name for path in result], ["002", "010"])

    def test_get_music_directory_returns_path_for_existing_song(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            expected_dir = _create_music_dir(root, "001")
            inspector = POP909Inspector(root)

            self.assertEqual(inspector.get_music_directory("001"), expected_dir)

    def test_get_music_directory_raises_for_missing_song(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            inspector = POP909Inspector(Path(tmpdir))

            with self.assertRaises(FileNotFoundError):
                inspector.get_music_directory("999")

    def test_count_music_counts_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _create_music_dir(root, "001")
            _create_music_dir(root, "002")

            inspector = POP909Inspector(root)

            self.assertEqual(inspector.count_music(), 2)

    def test_validate_structure_returns_empty_mapping_when_structure_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _create_music_dir(root, "001")

            inspector = POP909Inspector(root)

            self.assertEqual(inspector.validate_structure(), {})

    def test_validate_structure_reports_missing_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            music_dir = _create_music_dir(root, "001")
            (music_dir / "beat_audio.txt").unlink()
            (music_dir / "versions" / "001-v1.mid").unlink()
            (music_dir / "versions").rmdir()

            inspector = POP909Inspector(root)
            result = inspector.validate_structure()

            self.assertEqual(
                result,
                {
                    "001": ["beat_audio.txt", "versions/"],
                },
            )

    def test_generate_summary_report_returns_structured_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _create_music_dir(root, "001")
            _create_music_dir(root, "002", with_expected_files=False, with_versions_dir=False)

            inspector = POP909Inspector(root)
            summary = inspector.generate_summary_report()

            self.assertIsInstance(summary, DatasetSummary)
            self.assertEqual(summary.dataset_path, root)
            self.assertTrue(summary.exists)
            self.assertEqual(summary.music_count, 2)
            self.assertEqual(summary.valid_music_directories, 1)
            self.assertEqual(
                summary.invalid_directories,
                {
                    "002": [
                        "002.mid",
                        "beat_audio.txt",
                        "beat_midi.txt",
                        "chord_audio.txt",
                        "chord_midi.txt",
                        "key_audio.txt",
                        "versions/",
                    ]
                },
            )

    def test_print_summary_writes_human_readable_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _create_music_dir(root, "001")
            inspector = POP909Inspector(root)

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                inspector.print_summary()

            output = buffer.getvalue()
            self.assertIn("Dataset: POP909", output)
            self.assertIn(f"Caminho: {root.as_posix()}", output)
            self.assertIn("Dataset encontrado: Sim", output)
            self.assertIn("Numero de musicas: 1", output)
            self.assertIn("Diretorios validos: 1", output)
            self.assertIn("Diretorios invalidos: 0", output)

    def test_export_report_writes_markdown_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _create_music_dir(root, "001")
            _create_music_dir(root, "002", with_expected_files=False, with_versions_dir=False)
            inspector = POP909Inspector(root)
            output_path = root / "reports" / "inspection.md"

            inspector.export_report(output_path)

            content = output_path.read_text(encoding="utf-8")
            self.assertTrue(output_path.exists())
            self.assertIn("# Relatorio de Inspecao do POP909", content)
            self.assertIn("- Numero de musicas: 2", content)
            self.assertIn("- Numero de diretorios validos: 1", content)
            self.assertIn("- Numero de diretorios invalidos: 1", content)
            self.assertIn("- Data da inspecao: ", content)
            self.assertIn("### 002", content)
            self.assertIn("- `002.mid`", content)
            self.assertIn("- `versions/`", content)


if __name__ == "__main__":
    unittest.main()
