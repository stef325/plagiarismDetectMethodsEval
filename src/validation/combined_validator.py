"""Validador de transformações combinadas."""

from __future__ import annotations

from preprocessing.representation.combined_representation import CombinedRepresentation

from ._helpers import (
    COMBINED_COMPONENTS,
    HARMONY_TRANSFORMATIONS,
    MELODY_TRANSFORMATIONS,
    RHYTHM_TRANSFORMATIONS,
    parse_segment_identifier,
    parse_parameters,
    preserved_components_for_combination,
)
from ._models import ValidationResult


class CombinedValidator:
    """Valida transformações combinadas de melodia, harmonia e ritmo."""

    def validate(
        self,
        original: CombinedRepresentation,
        transformed: CombinedRepresentation,
        metadata: dict[str, object],
    ) -> ValidationResult:
        """Valida se apenas os componentes previstos foram alterados."""

        song_id, segment_id = parse_segment_identifier(original.segment_file)
        combination = str(metadata.get("combination", ""))
        parameters = parse_parameters(metadata)

        try:
            self._validate_combination(combination)
            self._validate_parameters(combination, metadata)
            self._validate_components(original, transformed, combination)
        except ValueError as error:
            return ValidationResult(
                song_id=song_id,
                segment_id=segment_id,
                transformation_type=combination,
                expected_changed_components=COMBINED_COMPONENTS.get(combination, ()),
                preserved_components=preserved_components_for_combination(combination)
                if combination in COMBINED_COMPONENTS
                else (),
                parameters=parameters,
                status="FAIL",
                error_message=str(error),
            )

        return ValidationResult(
            song_id=song_id,
            segment_id=segment_id,
            transformation_type=combination,
            expected_changed_components=COMBINED_COMPONENTS[combination],
            preserved_components=preserved_components_for_combination(combination),
            parameters=parameters,
        )

    def _validate_combination(self, combination: str) -> None:
        """Valida se a combinação pertence ao conjunto suportado."""

        if combination not in COMBINED_COMPONENTS:
            raise ValueError(f"Combinação inválida: {combination}")

    def _validate_parameters(
        self,
        combination: str,
        metadata: dict[str, object],
    ) -> None:
        """Valida se os parâmetros individuais foram registrados."""

        parameters = metadata.get("parameters")
        individual_transformations = metadata.get("individual_transformations")

        if not isinstance(parameters, dict) or not parameters:
            raise ValueError("Os parâmetros combinados não foram registrados.")
        if not isinstance(individual_transformations, dict) or not individual_transformations:
            raise ValueError("As transformações individuais não foram registradas.")

        component_transformations = {
            "melody": MELODY_TRANSFORMATIONS,
            "harmony": HARMONY_TRANSFORMATIONS,
            "rhythm": RHYTHM_TRANSFORMATIONS,
        }
        expected_components = set(COMBINED_COMPONENTS[combination])
        if set(parameters) != expected_components:
            unexpected_components = sorted(set(parameters) - expected_components)
            missing_components = sorted(expected_components - set(parameters))
            parts = []
            if unexpected_components:
                parts.append("Componentes combinados inválidos: " + ", ".join(unexpected_components))
            if missing_components:
                parts.append(
                    "Componentes combinados ausentes: " + ", ".join(missing_components)
                )
            raise ValueError(" ".join(parts))

        for component, spec in parameters.items():
            if not isinstance(spec, dict):
                raise ValueError(f"Especificação inválida para {component}.")

            transformation_name = str(spec.get("transformation", ""))
            component_parameters = spec.get("parameters", {})
            if not isinstance(component_parameters, dict):
                raise ValueError(f"Parâmetros inválidos para {component}.")

            expected_names = component_transformations.get(component)
            if expected_names is None:
                raise ValueError(f"Componente inválido: {component}.")
            if transformation_name not in expected_names:
                raise ValueError(
                    f"Transformação inválida para {component}: {transformation_name}"
                )

            missing_keys = [
                key for key in expected_names[transformation_name] if key not in component_parameters
            ]
            if missing_keys:
                raise ValueError(
                    f"Parâmetros obrigatórios ausentes em {component}: "
                    + ", ".join(sorted(missing_keys))
                )

            if individual_transformations.get(component) != transformation_name:
                raise ValueError(
                    f"Transformação individual não registrada corretamente para {component}."
                )

        if set(individual_transformations) != set(parameters):
            raise ValueError(
                "As transformações individuais não correspondem aos componentes registrados."
            )

    def _validate_components(
        self,
        original: CombinedRepresentation,
        transformed: CombinedRepresentation,
        combination: str,
    ) -> None:
        """Valida se apenas os componentes esperados foram alterados."""

        changed_components = set(COMBINED_COMPONENTS[combination])

        if "melody" in changed_components and transformed.melody == original.melody:
            raise ValueError("A melodia não sofreu alteração.")
        if "harmony" in changed_components and transformed.harmony == original.harmony:
            raise ValueError("A harmonia não sofreu alteração.")
        if "rhythm" in changed_components and transformed.rhythm == original.rhythm:
            raise ValueError("O ritmo não sofreu alteração.")

        if "melody" not in changed_components and transformed.melody != original.melody:
            raise ValueError("A melodia foi alterada indevidamente.")
        if "harmony" not in changed_components and transformed.harmony != original.harmony:
            raise ValueError("A harmonia foi alterada indevidamente.")
        if "rhythm" not in changed_components and transformed.rhythm != original.rhythm:
            raise ValueError("O ritmo foi alterado indevidamente.")
