"""Transformação combinada de melodia e ritmo."""

from __future__ import annotations

from preprocessing.representation.combined_representation import CombinedRepresentation
from preprocessing.representation.harmony_representation import HarmonyRepresentation
from preprocessing.representation.melody_representation import MelodyRepresentation
from preprocessing.representation.rhythm_representation import RhythmRepresentation
from transformations.melody import (
    IntervalModificationTransformation,
    OrnamentationTransformation,
    SimplificationTransformation as MelodySimplificationTransformation,
    TranspositionTransformation,
)
from transformations.rhythm import (
    DurationScalingTransformation,
    PartialRhythmModificationTransformation,
    TempoChangeTransformation,
)


class MelodyRhythmTransformation:
    """Aplica uma transformação melódica e uma rítmica na mesma execução."""

    def transform(
        self,
        melody: MelodyRepresentation,
        harmony: HarmonyRepresentation,
        rhythm: RhythmRepresentation,
        melody_transformation: str,
        melody_parameters: dict[str, object],
        rhythm_transformation: str,
        rhythm_parameters: dict[str, object],
        random_seed: int,
    ) -> CombinedRepresentation:
        """Aplica as transformações solicitadas sem modificar os objetos de entrada."""

        transformed_melody = _apply_melody_transformation(
            melody,
            melody_transformation,
            melody_parameters,
            random_seed,
        )
        transformed_rhythm = _apply_rhythm_transformation(
            rhythm,
            rhythm_transformation,
            rhythm_parameters,
            random_seed,
        )
        return CombinedRepresentation(
            segment_file=melody.segment_file,
            melody=transformed_melody,
            harmony=harmony,
            rhythm=transformed_rhythm,
        )


def _apply_melody_transformation(
    melody: MelodyRepresentation,
    transformation_name: str,
    parameters: dict[str, object],
    random_seed: int,
) -> MelodyRepresentation:
    """Executa a transformação melódica selecionada."""

    transform = transformation_name.lower().strip()
    if transform == "transpose":
        return TranspositionTransformation().transform(melody, semitones=int(parameters["semitones"]))
    if transform == "interval_modification":
        return IntervalModificationTransformation().transform(
            melody,
            strength=float(parameters["strength"]),
            random_seed=random_seed,
        )
    if transform == "ornamentation":
        return OrnamentationTransformation().transform(
            melody,
            density=float(parameters["density"]),
            random_seed=random_seed,
        )
    if transform == "simplification":
        return MelodySimplificationTransformation().transform(
            melody,
            strength=float(parameters["strength"]),
            random_seed=random_seed,
        )
    raise ValueError(f"Transformação melódica não suportada: {transformation_name}")


def _apply_rhythm_transformation(
    rhythm: RhythmRepresentation,
    transformation_name: str,
    parameters: dict[str, object],
    random_seed: int,
) -> RhythmRepresentation:
    """Executa a transformação rítmica selecionada."""

    transform = transformation_name.lower().strip()
    if transform == "tempo_change":
        return TempoChangeTransformation().transform(
            rhythm,
            tempo_factor=float(parameters["tempo_factor"]),
        )
    if transform == "duration_scaling":
        return DurationScalingTransformation().transform(
            rhythm,
            duration_factor=float(parameters["duration_factor"]),
        )
    if transform == "partial_rhythm_modification":
        return PartialRhythmModificationTransformation().transform(
            rhythm,
            strength=float(parameters["strength"]),
            random_seed=random_seed,
        )
    raise ValueError(f"Transformação rítmica não suportada: {transformation_name}")
