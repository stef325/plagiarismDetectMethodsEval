"""Validador de transformações harmônicas."""

from __future__ import annotations

from preprocessing.representation.combined_representation import CombinedRepresentation
from preprocessing.representation.harmony_representation import HarmonyRepresentation

from ._helpers import HARMONY_TRANSFORMATIONS, parse_segment_identifier, parse_parameters
from ._models import ValidationResult


class HarmonyValidator:
    """Valida transformações aplicadas apenas à harmonia."""

    def validate(
        self,
        original: CombinedRepresentation,
        transformed: HarmonyRepresentation,
        metadata: dict[str, object],
    ) -> ValidationResult:
        """Valida se somente a harmonia foi alterada."""

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
                expected_changed_components=("harmony",),
                preserved_components=("melody", "rhythm"),
                parameters=parameters,
                status="FAIL",
                error_message=str(error),
            )

        return ValidationResult(
            song_id=song_id,
            segment_id=segment_id,
            transformation_type=transformation,
            expected_changed_components=("harmony",),
            preserved_components=("melody", "rhythm"),
            parameters=parameters,
        )

    def _validate_transformation(self, transformation: str) -> None:
        """Valida se a transformação pertence ao conjunto suportado."""

        if transformation not in HARMONY_TRANSFORMATIONS:
            raise ValueError(f"Transformação harmônica inválida: {transformation}")

    def _validate_parameters(self, transformation: str, parameters: dict[str, object]) -> None:
        """Valida se os parâmetros obrigatórios estão presentes."""

        required_keys = HARMONY_TRANSFORMATIONS[transformation]
        missing_keys = [key for key in required_keys if key not in parameters]
        if missing_keys:
            raise ValueError(
                "Parâmetros obrigatórios ausentes: " + ", ".join(sorted(missing_keys))
            )

    def _validate_change(
        self,
        original: CombinedRepresentation,
        transformed: HarmonyRepresentation,
    ) -> None:
        """Valida se a harmonia de fato mudou."""

        if transformed == original.harmony:
            raise ValueError("A harmonia não sofreu alteração.")
