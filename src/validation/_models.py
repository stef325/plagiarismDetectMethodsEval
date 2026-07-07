"""Modelos compartilhados para validação das transformações."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ValidationResult:
    """Resultado de uma validação de transformação."""

    song_id: str
    segment_id: str
    transformation_type: str
    expected_changed_components: tuple[str, ...]
    preserved_components: tuple[str, ...]
    parameters: dict[str, Any] = field(default_factory=dict)
    status: str = "PASS"
    error_message: str = ""

    def to_row(self) -> dict[str, str]:
        """Converte o resultado para uma linha de CSV."""

        return {
            "song_id": self.song_id,
            "segment_id": self.segment_id,
            "transformation_type": self.transformation_type,
            "expected_changed_components": ", ".join(self.expected_changed_components),
            "preserved_components": ", ".join(self.preserved_components),
            "parameters": _format_parameters(self.parameters),
            "result": self.status,
            "error_message": self.error_message,
        }


def _format_parameters(parameters: dict[str, Any]) -> str:
    """Serializa parâmetros em JSON legível."""

    import json

    return json.dumps(parameters, ensure_ascii=False, sort_keys=True)
