from __future__ import annotations

import pytest

from metrics.harmony.chord_ngram_similarity import ChordNGramSimilarityMetric
from metrics.harmony.harmonic_edit_distance import HarmonicEditDistanceMetric
from metrics.harmony.pitch_class_similarity import PitchClassSimilarityMetric

from tests.metrics._helpers import build_harmony_representation, record_metric_value


@pytest.mark.metric_case(
    metric="harmony_chord_ngram_similarity",
    case="progressões iguais",
    expected="similaridade máxima",
)
def test_chord_ngram_similarity_identical(request) -> None:
    original = build_harmony_representation(["C4-E4-G4", "F4-A4-C5", "G4-B4-D5"])
    transformed = build_harmony_representation(["C4-E4-G4", "F4-A4-C5", "G4-B4-D5"])

    value = ChordNGramSimilarityMetric().compute(original, transformed, n=2)

    record_metric_value(request, value)
    assert value == pytest.approx(1.0)


@pytest.mark.metric_case(
    metric="harmony_chord_ngram_similarity",
    case="substituicao simples",
    expected="similaridade alta",
)
def test_chord_ngram_similarity_partial_change(request) -> None:
    original = build_harmony_representation(["C4-E4-G4", "F4-A4-C5", "G4-B4-D5"])
    transformed = build_harmony_representation(["Am4-C5-E5", "F4-A4-C5", "G4-B4-D5"])

    value = ChordNGramSimilarityMetric().compute(original, transformed, n=2)

    record_metric_value(request, value)
    assert 0.0 <= value <= 1.0
    assert value < 1.0


@pytest.mark.metric_case(
    metric="harmony_chord_ngram_similarity",
    case="sequencia vazia",
    expected="similaridade máxima",
)
def test_chord_ngram_similarity_empty_sequences(request) -> None:
    original = build_harmony_representation([])
    transformed = build_harmony_representation([])

    value = ChordNGramSimilarityMetric().compute(original, transformed, n=2)

    record_metric_value(request, value)
    assert value == pytest.approx(1.0)


@pytest.mark.metric_case(
    metric="harmony_chord_ngram_similarity",
    case="parametro n invalido",
    expected="ValueError",
)
def test_chord_ngram_similarity_rejects_invalid_n() -> None:
    original = build_harmony_representation(["C4-E4-G4", "F4-A4-C5"])
    transformed = build_harmony_representation(["C4-E4-G4", "F4-A4-C5"])

    with pytest.raises(ValueError):
        ChordNGramSimilarityMetric().compute(original, transformed, n=0)


@pytest.mark.metric_case(
    metric="harmony_harmonic_edit_distance",
    case="progressões iguais",
    expected="similaridade máxima",
)
def test_harmonic_edit_distance_identical(request) -> None:
    original = build_harmony_representation(["C4-E4-G4", "F4-A4-C5", "G4-B4-D5"])
    transformed = build_harmony_representation(["C4-E4-G4", "F4-A4-C5", "G4-B4-D5"])

    value = HarmonicEditDistanceMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert value == pytest.approx(1.0)


@pytest.mark.metric_case(
    metric="harmony_harmonic_edit_distance",
    case="reharmonizacao",
    expected="similaridade intermediaria",
)
def test_harmonic_edit_distance_reharmonization(request) -> None:
    original = build_harmony_representation(["C4-E4-G4", "F4-A4-C5", "G4-B4-D5"])
    transformed = build_harmony_representation(["Dm4-F4-A4", "Bb4-D5-F5", "C4-E4-G4"])

    value = HarmonicEditDistanceMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert 0.0 <= value <= 1.0
    assert value < 1.0


@pytest.mark.metric_case(
    metric="harmony_harmonic_edit_distance",
    case="sequencia vazia",
    expected="similaridade máxima",
)
def test_harmonic_edit_distance_empty_sequences(request) -> None:
    original = build_harmony_representation([])
    transformed = build_harmony_representation([])

    value = HarmonicEditDistanceMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert value == pytest.approx(1.0)


@pytest.mark.metric_case(
    metric="harmony_pitch_class_similarity",
    case="progressões iguais",
    expected="similaridade máxima",
)
def test_pitch_class_similarity_identical(request) -> None:
    original = build_harmony_representation(["C4-E4-G4", "F4-A4-C5"])
    transformed = build_harmony_representation(["C4-E4-G4", "F4-A4-C5"])

    value = PitchClassSimilarityMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert value == pytest.approx(1.0)


@pytest.mark.metric_case(
    metric="harmony_pitch_class_similarity",
    case="substituicao simples",
    expected="similaridade alta",
)
def test_pitch_class_similarity_partial_change(request) -> None:
    original = build_harmony_representation(["C4-E4-G4-B4", "F4-A4-C5-E5"])
    transformed = build_harmony_representation(["C4-E4-G4", "F4-A4-C5"])

    value = PitchClassSimilarityMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert 0.0 <= value <= 1.0
    assert value < 1.0


@pytest.mark.metric_case(
    metric="harmony_pitch_class_similarity",
    case="sequencia completamente diferente",
    expected="similaridade baixa",
)
def test_pitch_class_similarity_completely_different(request) -> None:
    original = build_harmony_representation(["C4-E4-G4", "F4-A4-C5"])
    transformed = build_harmony_representation(["D4-F#4-A4", "E4-G#4-B4"])

    value = PitchClassSimilarityMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert value == pytest.approx(0.0)


@pytest.mark.metric_case(
    metric="harmony_pitch_class_similarity",
    case="sequencia vazia",
    expected="similaridade máxima",
)
def test_pitch_class_similarity_empty_sequences(request) -> None:
    original = build_harmony_representation([])
    transformed = build_harmony_representation([])

    value = PitchClassSimilarityMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert value == pytest.approx(1.0)
