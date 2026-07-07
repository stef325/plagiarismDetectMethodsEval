from __future__ import annotations

import pytest

from metrics.melody.edit_distance import EditDistanceMetric
from metrics.melody.interval_ngram_similarity import IntervalNGramSimilarityMetric
from metrics.melody.longest_common_subsequence import LongestCommonSubsequenceMetric

from tests.metrics._helpers import build_melody_representation, record_metric_value


@pytest.mark.metric_case(
    metric="melody_interval_ngram_similarity",
    case="sequencias identicas",
    expected="similaridade próxima de 1",
)
@pytest.mark.parametrize("n", [2, 3])
def test_interval_ngram_similarity_identical(request, n: int) -> None:
    original = build_melody_representation([60, 62, 64, 65])
    transformed = build_melody_representation([60, 62, 64, 65])

    value = IntervalNGramSimilarityMetric().compute(original, transformed, n=n)

    record_metric_value(request, value)
    assert value == pytest.approx(1.0)


@pytest.mark.metric_case(
    metric="melody_interval_ngram_similarity",
    case="transposicao simples",
    expected="similaridade alta",
)
def test_interval_ngram_similarity_transposition_is_symmetric(request) -> None:
    original = build_melody_representation([60, 62, 64, 65])
    transformed = build_melody_representation([63, 65, 67, 68])

    value_ab = IntervalNGramSimilarityMetric().compute(original, transformed, n=2)
    value_ba = IntervalNGramSimilarityMetric().compute(transformed, original, n=2)

    record_metric_value(request, value_ab)
    assert value_ab == pytest.approx(1.0)
    assert value_ab == pytest.approx(value_ba)


@pytest.mark.metric_case(
    metric="melody_interval_ngram_similarity",
    case="alteracao de poucos intervalos",
    expected="similaridade intermediaria",
)
def test_interval_ngram_similarity_partial_change(request) -> None:
    original = build_melody_representation([60, 62, 64, 65])
    transformed = build_melody_representation([60, 63, 65, 66])

    value = IntervalNGramSimilarityMetric().compute(original, transformed, n=2)

    record_metric_value(request, value)
    assert 0.0 <= value <= 1.0
    assert value < 1.0
    assert value > 0.0


@pytest.mark.metric_case(
    metric="melody_interval_ngram_similarity",
    case="sequencias completamente diferentes",
    expected="similaridade baixa",
)
def test_interval_ngram_similarity_completely_different(request) -> None:
    original = build_melody_representation([60, 61, 62, 63])
    transformed = build_melody_representation([72, 70, 68, 66])

    value = IntervalNGramSimilarityMetric().compute(original, transformed, n=2)

    record_metric_value(request, value)
    assert value == pytest.approx(0.0)


@pytest.mark.metric_case(
    metric="melody_interval_ngram_similarity",
    case="sequencias vazias",
    expected="similaridade máxima",
)
def test_interval_ngram_similarity_empty_sequences(request) -> None:
    original = build_melody_representation([])
    transformed = build_melody_representation([])

    value = IntervalNGramSimilarityMetric().compute(original, transformed, n=2)

    record_metric_value(request, value)
    assert value == pytest.approx(1.0)


@pytest.mark.metric_case(
    metric="melody_interval_ngram_similarity",
    case="parametro n invalido",
    expected="ValueError",
)
def test_interval_ngram_similarity_rejects_invalid_n() -> None:
    original = build_melody_representation([60, 62, 64])
    transformed = build_melody_representation([60, 62, 64])

    with pytest.raises(ValueError):
        IntervalNGramSimilarityMetric().compute(original, transformed, n=0)


@pytest.mark.metric_case(
    metric="melody_longest_common_subsequence",
    case="sequencias identicas",
    expected="similaridade máxima",
)
def test_lcs_identical_sequences(request) -> None:
    original = build_melody_representation([60, 62, 64, 65])
    transformed = build_melody_representation([60, 62, 64, 65])

    value = LongestCommonSubsequenceMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert value == pytest.approx(1.0)


@pytest.mark.metric_case(
    metric="melody_longest_common_subsequence",
    case="transposicao simples",
    expected="similaridade máxima",
)
def test_lcs_transposition_is_symmetric(request) -> None:
    original = build_melody_representation([60, 62, 64, 65])
    transformed = build_melody_representation([63, 65, 67, 68])

    value_ab = LongestCommonSubsequenceMetric().compute(original, transformed)
    value_ba = LongestCommonSubsequenceMetric().compute(transformed, original)

    record_metric_value(request, value_ab)
    assert value_ab == pytest.approx(1.0)
    assert value_ab == pytest.approx(value_ba)


@pytest.mark.metric_case(
    metric="melody_longest_common_subsequence",
    case="sequencias totalmente diferentes",
    expected="similaridade baixa",
)
def test_lcs_completely_different(request) -> None:
    original = build_melody_representation([60, 61, 62, 63])
    transformed = build_melody_representation([72, 70, 68, 66])

    value = LongestCommonSubsequenceMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert value == pytest.approx(0.0)


@pytest.mark.metric_case(
    metric="melody_longest_common_subsequence",
    case="sequencias vazias",
    expected="similaridade máxima",
)
def test_lcs_empty_sequences(request) -> None:
    original = build_melody_representation([])
    transformed = build_melody_representation([])

    value = LongestCommonSubsequenceMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert value == pytest.approx(1.0)


@pytest.mark.metric_case(
    metric="melody_edit_distance",
    case="sequencias identicas",
    expected="similaridade máxima",
)
def test_edit_distance_identical_sequences(request) -> None:
    original = build_melody_representation([60, 62, 64, 65])
    transformed = build_melody_representation([60, 62, 64, 65])

    value = EditDistanceMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert value == pytest.approx(1.0)


@pytest.mark.metric_case(
    metric="melody_edit_distance",
    case="transposicao simples",
    expected="similaridade máxima",
)
def test_edit_distance_transposition_is_symmetric(request) -> None:
    original = build_melody_representation([60, 62, 64, 65])
    transformed = build_melody_representation([63, 65, 67, 68])

    value_ab = EditDistanceMetric().compute(original, transformed)
    value_ba = EditDistanceMetric().compute(transformed, original)

    record_metric_value(request, value_ab)
    assert value_ab == pytest.approx(1.0)
    assert value_ab == pytest.approx(value_ba)


@pytest.mark.metric_case(
    metric="melody_edit_distance",
    case="sequencias diferentes",
    expected="similaridade baixa",
)
def test_edit_distance_completely_different(request) -> None:
    original = build_melody_representation([60, 61, 62, 63])
    transformed = build_melody_representation([72, 70, 68, 66])

    value = EditDistanceMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert value == pytest.approx(0.0)


@pytest.mark.metric_case(
    metric="melody_edit_distance",
    case="sequencias vazias",
    expected="similaridade máxima",
)
def test_edit_distance_empty_sequences(request) -> None:
    original = build_melody_representation([])
    transformed = build_melody_representation([])

    value = EditDistanceMetric().compute(original, transformed)

    record_metric_value(request, value)
    assert value == pytest.approx(1.0)
