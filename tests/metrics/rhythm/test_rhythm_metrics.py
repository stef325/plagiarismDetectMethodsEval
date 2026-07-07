from __future__ import annotations

import pytest

from metrics.rhythm.ioi_similarity import IoISimilarityMetric
from metrics.rhythm.rhythm_ngram_similarity import RhythmNGramSimilarityMetric
from metrics.rhythm.rhythmic_edit_distance import RhythmicEditDistanceMetric

from tests.metrics._helpers import build_rhythm_representation, record_metric_value


@pytest.mark.metric_case(
    metric="rhythm_rhythm_ngram_similarity",
    case="padrao identico",
    expected="similaridade máxima",
)
def test_rhythm_ngram_similarity_identical(request) -> None:
    original = build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])
    transformed = build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])

    value = RhythmNGramSimilarityMetric().compute(original, transformed, n=2)

    record_metric_value(request, value)
    assert value == pytest.approx(1.0)


@pytest.mark.metric_case(
    metric="rhythm_rhythm_ngram_similarity",
    case="alteracao de andamento",
    expected="similaridade alta",
)
def test_rhythm_ngram_similarity_tempo_change(request) -> None:
    original = build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])
    transformed = build_rhythm_representation([(0.0, 0.4), (0.4, 0.4), (0.8, 0.4)])

    value = RhythmNGramSimilarityMetric().compute(original, transformed, n=2)

    record_metric_value(request, value)
    assert 0.0 <= value <= 1.0


@pytest.mark.metric_case(
    metric="rhythm_rhythm_ngram_similarity",
    case="alteracao parcial",
    expected="similaridade intermediaria",
)
def test_rhythm_ngram_similarity_partial_change(request) -> None:
    original = build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])
    transformed = build_rhythm_representation([(0.0, 0.5), (0.5, 0.25), (0.75, 0.5)])

    value = RhythmNGramSimilarityMetric().compute(original, transformed, n=2)

    record_metric_value(request, value)
    assert 0.0 <= value <= 1.0
    assert value < 1.0


@pytest.mark.metric_case(
    metric="rhythm_rhythm_ngram_similarity",
    case="padrao completamente diferente",
    expected="similaridade baixa",
)
def test_rhythm_ngram_similarity_completely_different(request) -> None:
    original = build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])
    transformed = build_rhythm_representation([(0.0, 0.25), (0.35, 0.55), (0.95, 0.15)])

    value = RhythmNGramSimilarityMetric().compute(original, transformed, n=2)

    record_metric_value(request, value)
    assert value == pytest.approx(0.0)


@pytest.mark.metric_case(
    metric="rhythm_rhythm_ngram_similarity",
    case="sequencia vazia",
    expected="similaridade máxima",
)
def test_rhythm_ngram_similarity_empty_sequences(request) -> None:
    original = build_rhythm_representation([])
    transformed = build_rhythm_representation([])

    value = RhythmNGramSimilarityMetric().compute(original, transformed, n=2)

    record_metric_value(request, value)
    assert value == pytest.approx(1.0)


@pytest.mark.metric_case(
    metric="rhythm_rhythm_ngram_similarity",
    case="parametro n invalido",
    expected="ValueError",
)
def test_rhythm_ngram_similarity_rejects_invalid_n() -> None:
    original = build_rhythm_representation([(0.0, 0.5), (0.5, 0.5)])
    transformed = build_rhythm_representation([(0.0, 0.5), (0.5, 0.5)])

    with pytest.raises(ValueError):
        RhythmNGramSimilarityMetric().compute(original, transformed, n=0)


@pytest.mark.metric_case(
    metric="rhythm_ioi_similarity",
    case="padrao identico",
    expected="similaridade máxima",
)
def test_ioi_similarity_identical(request) -> None:
    original = build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])
    transformed = build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])

    value = IoISimilarityMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert value == pytest.approx(1.0)


@pytest.mark.metric_case(
    metric="rhythm_ioi_similarity",
    case="alteracao de andamento",
    expected="similaridade alta",
)
def test_ioi_similarity_tempo_change(request) -> None:
    original = build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])
    transformed = build_rhythm_representation([(0.0, 0.4), (0.4, 0.4), (0.8, 0.4)])

    value = IoISimilarityMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert 0.0 <= value <= 1.0
    assert value == pytest.approx(1.0)


@pytest.mark.metric_case(
    metric="rhythm_ioi_similarity",
    case="alteracao parcial",
    expected="similaridade intermediaria",
)
def test_ioi_similarity_partial_change(request) -> None:
    original = build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])
    transformed = build_rhythm_representation([(0.0, 0.5), (0.5, 0.25), (0.75, 0.5)])

    value = IoISimilarityMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert 0.0 <= value <= 1.0
    assert value < 1.0


@pytest.mark.metric_case(
    metric="rhythm_ioi_similarity",
    case="sequencia vazia",
    expected="similaridade máxima",
)
def test_ioi_similarity_empty_sequences(request) -> None:
    original = build_rhythm_representation([])
    transformed = build_rhythm_representation([])

    value = IoISimilarityMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert value == pytest.approx(1.0)


@pytest.mark.metric_case(
    metric="rhythm_rhythmic_edit_distance",
    case="padrao identico",
    expected="similaridade máxima",
)
def test_rhythmic_edit_distance_identical(request) -> None:
    original = build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])
    transformed = build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])

    value = RhythmicEditDistanceMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert value == pytest.approx(1.0)


@pytest.mark.metric_case(
    metric="rhythm_rhythmic_edit_distance",
    case="alteracao de andamento",
    expected="similaridade alta",
)
def test_rhythmic_edit_distance_tempo_change(request) -> None:
    original = build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])
    transformed = build_rhythm_representation([(0.0, 0.4), (0.4, 0.4), (0.8, 0.4)])

    value = RhythmicEditDistanceMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert 0.0 <= value <= 1.0


@pytest.mark.metric_case(
    metric="rhythm_rhythmic_edit_distance",
    case="alteracao parcial",
    expected="similaridade intermediaria",
)
def test_rhythmic_edit_distance_partial_change(request) -> None:
    original = build_rhythm_representation([(0.0, 0.5), (0.5, 0.5), (1.0, 0.5)])
    transformed = build_rhythm_representation([(0.0, 0.5), (0.5, 0.25), (0.75, 0.5)])

    value = RhythmicEditDistanceMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert 0.0 <= value <= 1.0
    assert value < 1.0


@pytest.mark.metric_case(
    metric="rhythm_rhythmic_edit_distance",
    case="sequencia vazia",
    expected="similaridade máxima",
)
def test_rhythmic_edit_distance_empty_sequences(request) -> None:
    original = build_rhythm_representation([])
    transformed = build_rhythm_representation([])

    value = RhythmicEditDistanceMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert value == pytest.approx(1.0)
