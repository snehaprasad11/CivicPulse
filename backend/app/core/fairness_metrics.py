from __future__ import annotations

import numpy as np

from app.models.schemas import FairnessMetrics, GroupMetric


def _safe_rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def _accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float | None:
    if len(y_true) == 0:
        return None
    return float(np.mean(y_true == y_pred))


def compute_fairness_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    groups: np.ndarray,
    positive_label: int = 1,
) -> FairnessMetrics:
    """Compute standard group fairness metrics from first principles."""
    unique_groups = sorted(str(group) for group in np.unique(groups))
    group_metrics: list[GroupMetric] = []

    for group in unique_groups:
        mask = groups.astype(str) == group
        group_true = y_true[mask]
        group_pred = y_pred[mask]

        positives = group_pred == positive_label
        actual_positive = group_true == positive_label
        actual_negative = group_true != positive_label

        selection_rate = float(np.mean(positives)) if len(group_pred) else 0.0
        tpr = _safe_rate(int(np.sum(positives & actual_positive)), int(np.sum(actual_positive)))
        fpr = _safe_rate(int(np.sum(positives & actual_negative)), int(np.sum(actual_negative)))

        group_metrics.append(
            GroupMetric(
                group=group,
                count=int(np.sum(mask)),
                selection_rate=selection_rate,
                true_positive_rate=tpr,
                false_positive_rate=fpr,
                accuracy=_accuracy(group_true, group_pred),
            )
        )

    reference = max(group_metrics, key=lambda metric: metric.selection_rate)
    min_selection = min(metric.selection_rate for metric in group_metrics)
    max_selection = max(metric.selection_rate for metric in group_metrics)
    disparate_impact = None if max_selection == 0 else min_selection / max_selection

    valid_tprs = [metric.true_positive_rate for metric in group_metrics if metric.true_positive_rate is not None]
    valid_fprs = [metric.false_positive_rate for metric in group_metrics if metric.false_positive_rate is not None]
    equal_opp = None if not valid_tprs else max(valid_tprs) - min(valid_tprs)
    equalized_odds = None
    if valid_tprs and valid_fprs:
        equalized_odds = max(max(valid_tprs) - min(valid_tprs), max(valid_fprs) - min(valid_fprs))

    return FairnessMetrics(
        reference_group=reference.group,
        disparate_impact_ratio=disparate_impact,
        demographic_parity_difference=max_selection - min_selection,
        equal_opportunity_difference=equal_opp,
        equalized_odds_difference=equalized_odds,
        group_metrics=group_metrics,
    )
