from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from experiment.validate_transformations import validate_transformations
from preprocessing.representation.combined_representation import CombinedRepresentation
from preprocessing.representation.harmony_representation import HarmonyRepresentation
from preprocessing.representation.melody_representation import MelodyRepresentation
from preprocessing.representation.rhythm_representation import RhythmRepresentation
from validation.combined_validator import CombinedValidator
from validation.harmony_validator import HarmonyValidator
from validation.melody_validator import MelodyValidator
from validation.rhythm_validator import RhythmValidator


def _build_combined_representation() -> CombinedRepresentation:
    return CombinedRepresentation(
        segment_file="001_segment_01.mid",
        melody=MelodyRepresentation.from_dict(
            {
                "segment_file": "001_segment_01.mid",
                "melody": [
                    {"pitch": 60, "duration": 0.5},
                    {"pitch": 62, "duration": 0.5},
                    {"pitch": 64, "duration": 1.0},
                ],
            }
        ),
        harmony=HarmonyRepresentation.from_dict(
            {
                "segment_file": "001_segment_01.mid",
                "harmony": [
                    {"start": 0.0, "end": 1.0, "chord": "C"},
                    {"start": 1.0, "end": 2.0, "chord": "G"},
                ],
            }
        ),
        rhythm=RhythmRepresentation.from_dict(
            {
                "segment_file": "001_segment_01.mid",
                "rhythm": [
                    {"onset": 0.0, "duration": 0.5},
                    {"onset": 0.5, "duration": 0.5},
                    {"onset": 1.0, "duration": 1.0},
                ],
            }
        ),
    )


def _build_individual_metadata(transformation: str, parameters: dict[str, object]) -> dict[str, object]:
    return {
        "transformation": transformation,
        "parameters": parameters,
    }


def _build_combined_metadata(
    combination: str,
    melody_transformation: str,
    melody_parameters: dict[str, object],
    harmony_transformation: str,
    harmony_parameters: dict[str, object],
    rhythm_transformation: str | None = None,
    rhythm_parameters: dict[str, object] | None = None,
) -> dict[str, object]:
    parameters = {
        "combination": combination,
        "parameters": {
            "melody": {
                "transformation": melody_transformation,
                "parameters": melody_parameters,
            },
            "harmony": {
                "transformation": harmony_transformation,
                "parameters": harmony_parameters,
            },
        },
        "individual_transformations": {
            "melody": melody_transformation,
            "harmony": harmony_transformation,
        },
    }

    if rhythm_transformation is not None and rhythm_parameters is not None:
        parameters["parameters"]["rhythm"] = {
            "transformation": rhythm_transformation,
            "parameters": rhythm_parameters,
        }
        parameters["individual_transformations"]["rhythm"] = rhythm_transformation

    return parameters


class TransformationValidatorTestCase(unittest.TestCase):
    def test_melody_validator_passes_for_valid_change(self) -> None:
        original = _build_combined_representation()
        transformed = MelodyRepresentation.from_dict(
            {
                "segment_file": original.segment_file,
                "melody": [
                    {"pitch": 62, "duration": 0.5},
                    {"pitch": 64, "duration": 0.5},
                    {"pitch": 66, "duration": 1.0},
                ],
            }
        )

        result = MelodyValidator().validate(
            original,
            transformed,
            _build_individual_metadata("transpose", {"semitones": 2}),
        )

        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.expected_changed_components, ("melody",))
        self.assertEqual(result.preserved_components, ("harmony", "rhythm"))

    def test_melody_validator_fails_when_parameters_are_missing(self) -> None:
        original = _build_combined_representation()
        transformed = MelodyRepresentation.from_dict(
            {
                "segment_file": original.segment_file,
                "melody": [
                    {"pitch": 62, "duration": 0.5},
                    {"pitch": 64, "duration": 0.5},
                    {"pitch": 66, "duration": 1.0},
                ],
            }
        )

        result = MelodyValidator().validate(
            original,
            transformed,
            _build_individual_metadata("transpose", {}),
        )

        self.assertEqual(result.status, "FAIL")
        self.assertIn("Parâmetros obrigatórios ausentes", result.error_message)

    def test_harmony_validator_passes_for_valid_change(self) -> None:
        original = _build_combined_representation()
        transformed = HarmonyRepresentation.from_dict(
            {
                "segment_file": original.segment_file,
                "harmony": [
                    {"start": 0.0, "end": 1.0, "chord": "Am"},
                    {"start": 1.0, "end": 2.0, "chord": "Em"},
                ],
            }
        )

        result = HarmonyValidator().validate(
            original,
            transformed,
            _build_individual_metadata("chord_substitution", {"strength": 0.25}),
        )

        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.expected_changed_components, ("harmony",))
        self.assertEqual(result.preserved_components, ("melody", "rhythm"))

    def test_harmony_validator_fails_when_component_is_not_changed(self) -> None:
        original = _build_combined_representation()

        result = HarmonyValidator().validate(
            original,
            original.harmony,
            _build_individual_metadata("chord_substitution", {"strength": 0.25}),
        )

        self.assertEqual(result.status, "FAIL")
        self.assertIn("A harmonia não sofreu alteração", result.error_message)

    def test_rhythm_validator_passes_for_valid_change(self) -> None:
        original = _build_combined_representation()
        transformed = RhythmRepresentation.from_dict(
            {
                "segment_file": original.segment_file,
                "rhythm": [
                    {"onset": 0.0, "duration": 0.4},
                    {"onset": 0.4, "duration": 0.4},
                    {"onset": 0.8, "duration": 0.8},
                ],
            }
        )

        result = RhythmValidator().validate(
            original,
            transformed,
            _build_individual_metadata("tempo_change", {"tempo_factor": 0.8}),
        )

        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.expected_changed_components, ("rhythm",))
        self.assertEqual(result.preserved_components, ("melody", "harmony"))

    def test_rhythm_validator_fails_when_parameters_are_missing(self) -> None:
        original = _build_combined_representation()
        transformed = RhythmRepresentation.from_dict(
            {
                "segment_file": original.segment_file,
                "rhythm": [
                    {"onset": 0.0, "duration": 0.4},
                    {"onset": 0.4, "duration": 0.4},
                    {"onset": 0.8, "duration": 0.8},
                ],
            }
        )

        result = RhythmValidator().validate(
            original,
            transformed,
            _build_individual_metadata("tempo_change", {}),
        )

        self.assertEqual(result.status, "FAIL")
        self.assertIn("Parâmetros obrigatórios ausentes", result.error_message)

    def test_combined_validator_passes_for_valid_combination(self) -> None:
        original = _build_combined_representation()
        transformed = CombinedRepresentation(
            segment_file=original.segment_file,
            melody=MelodyRepresentation.from_dict(
                {
                    "segment_file": original.segment_file,
                    "melody": [
                        {"pitch": 62, "duration": 0.5},
                        {"pitch": 64, "duration": 0.5},
                        {"pitch": 66, "duration": 1.0},
                    ],
                }
            ),
            harmony=HarmonyRepresentation.from_dict(
                {
                    "segment_file": original.segment_file,
                    "harmony": [
                        {"start": 0.0, "end": 1.0, "chord": "Am"},
                        {"start": 1.0, "end": 2.0, "chord": "Em"},
                    ],
                }
            ),
            rhythm=original.rhythm,
        )

        result = CombinedValidator().validate(
            original,
            transformed,
            _build_combined_metadata(
                combination="melody_harmony",
                melody_transformation="transpose",
                melody_parameters={"semitones": 2},
                harmony_transformation="chord_substitution",
                harmony_parameters={"strength": 0.25},
            ),
        )

        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.expected_changed_components, ("melody", "harmony"))
        self.assertEqual(result.preserved_components, ("rhythm",))

    def test_combined_validator_fails_when_unexpected_component_changes(self) -> None:
        original = _build_combined_representation()
        transformed = CombinedRepresentation(
            segment_file=original.segment_file,
            melody=MelodyRepresentation.from_dict(
                {
                    "segment_file": original.segment_file,
                    "melody": [
                        {"pitch": 62, "duration": 0.5},
                        {"pitch": 64, "duration": 0.5},
                        {"pitch": 66, "duration": 1.0},
                    ],
                }
            ),
            harmony=HarmonyRepresentation.from_dict(
                {
                    "segment_file": original.segment_file,
                    "harmony": [
                        {"start": 0.0, "end": 1.0, "chord": "Am"},
                        {"start": 1.0, "end": 2.0, "chord": "Em"},
                    ],
                }
            ),
            rhythm=RhythmRepresentation.from_dict(
                {
                    "segment_file": original.segment_file,
                    "rhythm": [
                        {"onset": 0.0, "duration": 0.4},
                        {"onset": 0.4, "duration": 0.4},
                        {"onset": 0.8, "duration": 0.8},
                    ],
                }
            ),
        )

        result = CombinedValidator().validate(
            original,
            transformed,
            _build_combined_metadata(
                combination="melody_harmony",
                melody_transformation="transpose",
                melody_parameters={"semitones": 2},
                harmony_transformation="chord_substitution",
                harmony_parameters={"strength": 0.25},
            ),
        )

        self.assertEqual(result.status, "FAIL")
        self.assertIn("O ritmo foi alterado indevidamente", result.error_message)


class ValidateTransformationsPipelineTestCase(unittest.TestCase):
    def test_validate_transformations_creates_report_and_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            representations_root = root / "data" / "processed" / "representations"
            transformations_root = root / "data" / "processed" / "transformations"
            validation_root = transformations_root / "validation"
            representations_root.mkdir(parents=True, exist_ok=True)

            original_payload = {
                "segment_file": "001_segment_01.mid",
                "melody": [
                    {"pitch": 60, "duration": 0.5},
                    {"pitch": 62, "duration": 0.5},
                ],
                "harmony": [
                    {"start": 0.0, "end": 1.0, "chord": "C"},
                ],
                "rhythm": [
                    {"onset": 0.0, "duration": 0.5},
                    {"onset": 0.5, "duration": 0.5},
                ],
            }
            (representations_root / "001_segment_01.json").write_text(
                json.dumps(original_payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            metadata_leaf = transformations_root / "melody" / "transpose" / "semitones_2"
            metadata_leaf.mkdir(parents=True, exist_ok=True)
            transformed_payload = {
                "segment_file": "001_segment_01.mid",
                "melody": [
                    {"pitch": 62, "duration": 0.5},
                    {"pitch": 64, "duration": 0.5},
                ],
                "transformation": "transpose",
                "parameters": {"semitones": 2},
            }
            (metadata_leaf / "001_segment_01.json").write_text(
                json.dumps(transformed_payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            with (metadata_leaf / "metadata.csv").open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=[
                        "song_id",
                        "segment_id",
                        "transformation",
                        "parameters",
                        "source_file",
                        "generated_file",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "song_id": "001",
                        "segment_id": "01",
                        "transformation": "transpose",
                        "parameters": json.dumps({"semitones": 2}, ensure_ascii=False),
                        "source_file": "001_segment_01.json",
                        "generated_file": "001_segment_01.json",
                    }
                )

            result = validate_transformations(
                transformations_path=transformations_root,
                representations_path=representations_root,
                output_path=validation_root,
            )

            self.assertEqual(result, validation_root)
            report_path = validation_root / "transformations_validation_report.md"
            self.assertTrue(report_path.exists())
            validation_csv = validation_root / "melody" / "transpose" / "semitones_2" / "validation.csv"
            self.assertTrue(validation_csv.exists())

            report_text = report_path.read_text(encoding="utf-8")
            self.assertIn("Validações aprovadas: 1", report_text)
            self.assertIn("PASS", report_text)

    def test_validate_transformations_reuses_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            representations_root = root / "data" / "processed" / "representations"
            transformations_root = root / "data" / "processed" / "transformations"
            validation_root = transformations_root / "validation"
            representations_root.mkdir(parents=True, exist_ok=True)

            original_payload = {
                "segment_file": "001_segment_01.mid",
                "melody": [
                    {"pitch": 60, "duration": 0.5},
                    {"pitch": 62, "duration": 0.5},
                ],
                "harmony": [
                    {"start": 0.0, "end": 1.0, "chord": "C"},
                ],
                "rhythm": [
                    {"onset": 0.0, "duration": 0.5},
                    {"onset": 0.5, "duration": 0.5},
                ],
            }
            (representations_root / "001_segment_01.json").write_text(
                json.dumps(original_payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            metadata_leaf = transformations_root / "melody" / "transpose" / "semitones_2"
            metadata_leaf.mkdir(parents=True, exist_ok=True)
            transformed_payload = {
                "segment_file": "001_segment_01.mid",
                "melody": [
                    {"pitch": 62, "duration": 0.5},
                    {"pitch": 64, "duration": 0.5},
                ],
                "transformation": "transpose",
                "parameters": {"semitones": 2},
            }
            (metadata_leaf / "001_segment_01.json").write_text(
                json.dumps(transformed_payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            with (metadata_leaf / "metadata.csv").open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=[
                        "song_id",
                        "segment_id",
                        "transformation",
                        "parameters",
                        "source_file",
                        "generated_file",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "song_id": "001",
                        "segment_id": "01",
                        "transformation": "transpose",
                        "parameters": json.dumps({"semitones": 2}, ensure_ascii=False),
                        "source_file": "001_segment_01.json",
                        "generated_file": "001_segment_01.json",
                    }
                )

            validate_transformations(
                transformations_path=transformations_root,
                representations_path=representations_root,
                output_path=validation_root,
            )

            with patch("experiment.validate_transformations.MelodyValidator.validate") as mocked_validate:
                validate_transformations(
                    transformations_path=transformations_root,
                    representations_path=representations_root,
                    output_path=validation_root,
                )

            mocked_validate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
