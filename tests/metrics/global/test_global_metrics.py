from __future__ import annotations

import pytest

from importlib import import_module

from tests.metrics._helpers import record_metric_value


global_metrics = import_module("metrics.global")


@pytest.mark.metric_case(
    metric="global_simple_average",
    case="metricas identicas",
    expected="similaridade máxima",
)
def test_simple_average_identical(request) -> None:
    metric = global_metrics.SimpleAverageMetric()

    value = metric.compute(
        melody_scores={"m1": 1.0, "m2": 1.0},
        harmony_scores={"h1": 1.0},
        rhythm_scores={"r1": 1.0},
    )

    record_metric_value(request, value)
    assert value == pytest.approx(1.0)


@pytest.mark.metric_case(
    metric="global_simple_average",
    case="metricas diferentes",
    expected="similaridade intermediaria",
)
def test_simple_average_different_scores(request) -> None:
    metric = global_metrics.SimpleAverageMetric()

    value = metric.compute(
        melody_scores={"m1": 1.0, "m2": 0.0},
        harmony_scores={"h1": 0.5},
        rhythm_scores={"r1": 0.25},
    )

    record_metric_value(request, value)
    assert 0.0 <= value <= 1.0
    assert value == pytest.approx(0.4375)


@pytest.mark.metric_case(
    metric="global_weighted_average",
    case="pesos validos",
    expected="similaridade ponderada calculada corretamente",
)
def test_weighted_average_valid_weights(request) -> None:
    metric = global_metrics.WeightedAverageMetric()

    value = metric.compute(
        melody_scores={"m1": 1.0},
        harmony_scores={"h1": 0.5},
        rhythm_scores={"r1": 0.25},
        weights={"melody": 0.4, "harmony": 0.35, "rhythm": 0.25},
    )

    record_metric_value(request, value)
    assert 0.0 <= value <= 1.0
    assert value == pytest.approx(0.6375)


@pytest.mark.metric_case(
    metric="global_weighted_average",
    case="pesos ausentes",
    expected="ValueError",
)
def test_weighted_average_rejects_missing_weights() -> None:
    metric = global_metrics.WeightedAverageMetric()

    with pytest.raises(ValueError):
        metric.compute(
            melody_scores={"m1": 1.0},
            harmony_scores={"h1": 1.0},
            rhythm_scores={"r1": 1.0},
            weights={"melody": 0.4, "harmony": 0.6},
        )


@pytest.mark.metric_case(
    metric="global_weighted_average",
    case="pesos negativos",
    expected="ValueError",
)
def test_weighted_average_rejects_negative_weights() -> None:
    metric = global_metrics.WeightedAverageMetric()

    with pytest.raises(ValueError):
        metric.compute(
            melody_scores={"m1": 1.0},
            harmony_scores={"h1": 1.0},
            rhythm_scores={"r1": 1.0},
            weights={"melody": 0.4, "harmony": -0.1, "rhythm": 0.7},
        )


@pytest.mark.metric_case(
    metric="global_weighted_average",
    case="soma dos pesos invalida",
    expected="ValueError",
)
def test_weighted_average_rejects_invalid_weight_sum() -> None:
    metric = global_metrics.WeightedAverageMetric()

    with pytest.raises(ValueError):
        metric.compute(
            melody_scores={"m1": 1.0},
            harmony_scores={"h1": 1.0},
            rhythm_scores={"r1": 1.0},
            weights={"melody": 0.4, "harmony": 0.4, "rhythm": 0.4},
        )
