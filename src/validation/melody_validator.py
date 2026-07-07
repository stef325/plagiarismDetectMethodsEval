"""Validador de transformações melódicas."""

from __future__ import annotations

from preprocessing.representation.combined_representation import CombinedRepresentation
from preprocessing.representation.melody_representation import MelodyRepresentation

from ._helpers import MELODY_TRANSFORMATIONS, parse_segment_identifier, parse_parameters
from ._models import ValidationResult


class MelodyValidator:
    """Valida transformações aplicadas apenas à melodia."""

    def validate(
        self,
        original: CombinedRepresentation,
        transformed: MelodyRepresentation,
        metadata: dict[str, object],
    ) -> ValidationResult:
        """Valida se somente a melodia foi alterada."""

        song_id, segment_id = parse_segment_identifier(original.segment_file)
        transformation = str(metadata.get("transformation", ""))
        parameters = parse_parameters(metadata)

        try:
            self._validate_transformation(transformation)
            self._validate_parameters(transformation, parameters)
            self._validate_change(original, transformed)
        except ValueError as error:
            return ValidationResult(
                song_id=song_id,
                segment_id=segment_id,
                transformation_type=transformation,
                expected_changed_components=("melody",),
                preserved_components=("harmony", "rhythm"),
                parameters=parameters,
                status="FAIL",
                error_message=str(error),
            )

        return ValidationResult(
            song_id=song_id,
            segment_id=segment_id,
            transformation_type=transformation,
            expected_changed_components=("melody",),
            preserved_components=("harmony", "rhythm"),
            parameters=parameters,
        )

    def _validate_transformation(self, transformation: str) -> None:
        """Valida se a transformação pertence ao conjunto suportado."""

        if transformation not in MELODY_TRANSFORMATIONS:
            raise ValueError(f"Transformação melódica inválida: {transformation}")

    def _validate_parameters(self, transformation: str, parameters: dict[str, object]) -> None:
        """Valida se os parâmetros obrigatórios estão presentes."""

        required_keys = MELODY_TRANSFORMATIONS[transformation]
        missing_keys = [key for key in required_keys if key not in parameters]
        if missing_keys:
            raise ValueError(
                "Parâmetros obrigatórios ausentes: " + ", ".join(sorted(missing_keys))
            )

    def _validate_change(
        self,
        original: CombinedRepresentation,
        transformed: MelodyRepresentation,
    ) -> None:
        """Valida se a melodia de fato mudou."""

        if transformed == original.melody:
            raise ValueError("A melodia não sofreu alteração.")
