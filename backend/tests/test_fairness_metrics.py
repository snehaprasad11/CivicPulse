import numpy as np

from app.core.fairness_metrics import compute_fairness_metrics


def test_disparate_impact_and_demographic_parity() -> None:
    y_true = np.array([1, 1, 1, 0, 1, 0])
    y_pred = np.array([1, 1, 0, 0, 0, 0])
    groups = np.array(["A", "A", "A", "B", "B", "B"])

    metrics = compute_fairness_metrics(y_true, y_pred, groups)

    assert round(metrics.disparate_impact_ratio or 0, 2) == 0.0
    assert round(metrics.demographic_parity_difference, 2) == 0.67
    assert metrics.reference_group == "A"


def test_equal_opportunity_difference() -> None:
    y_true = np.array([1, 1, 0, 0, 1, 1, 0, 0])
    y_pred = np.array([1, 0, 1, 0, 1, 1, 0, 0])
    groups = np.array(["A", "A", "A", "A", "B", "B", "B", "B"])

    metrics = compute_fairness_metrics(y_true, y_pred, groups)

    assert metrics.equal_opportunity_difference == 0.5
    assert metrics.equalized_odds_difference == 0.5
