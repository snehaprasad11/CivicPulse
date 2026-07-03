import numpy as np
import pandas as pd

from app.core.fairness_metrics import compute_fairness_metrics
from app.models.schemas import MitigationResult


def _accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(y_true == y_pred))


def simulate_threshold_mitigation(
    df: pd.DataFrame,
    target: str,
    protected_attribute: str,
    score_column: str | None,
    positive_label: int = 1,
) -> list[MitigationResult]:
    if not score_column or score_column not in df.columns:
        base_pred = df[target].astype(int).to_numpy()
        metrics = compute_fairness_metrics(
            y_true=df[target].astype(int).to_numpy(),
            y_pred=base_pred,
            groups=df[protected_attribute].astype(str).to_numpy(),
            positive_label=positive_label,
        )
        return [
            MitigationResult(
                strategy="No score column available",
                accuracy=1.0,
                demographic_parity_difference=metrics.demographic_parity_difference,
                equal_opportunity_difference=metrics.equal_opportunity_difference,
                notes="Upload model scores to simulate threshold-based mitigation.",
            )
        ]

    y_true = df[target].astype(int).to_numpy()
    groups = df[protected_attribute].astype(str).to_numpy()
    scores = df[score_column].astype(float).to_numpy()

    baseline_pred = (scores >= 0.5).astype(int)
    baseline_metrics = compute_fairness_metrics(y_true, baseline_pred, groups, positive_label)

    results = [
        MitigationResult(
            strategy="Baseline threshold",
            accuracy=_accuracy(y_true, baseline_pred),
            demographic_parity_difference=baseline_metrics.demographic_parity_difference,
            equal_opportunity_difference=baseline_metrics.equal_opportunity_difference,
            notes="Single 0.50 approval threshold applied to every group.",
        )
    ]

    target_rate = float(np.mean(baseline_pred == positive_label))
    adjusted_pred = np.zeros_like(baseline_pred)

    for group in np.unique(groups):
        mask = groups == group
        group_scores = scores[mask]
        threshold = float(np.quantile(group_scores, max(0.0, min(1.0, 1.0 - target_rate))))
        adjusted_pred[mask] = (group_scores >= threshold).astype(int)

    adjusted_metrics = compute_fairness_metrics(y_true, adjusted_pred, groups, positive_label)
    results.append(
        MitigationResult(
            strategy="Group threshold adjustment",
            accuracy=_accuracy(y_true, adjusted_pred),
            demographic_parity_difference=adjusted_metrics.demographic_parity_difference,
            equal_opportunity_difference=adjusted_metrics.equal_opportunity_difference,
            notes="Per-group thresholds target a shared selection rate. This is a simulation, not a policy recommendation.",
        )
    )

    reweighted_pred = baseline_pred.copy()
    lowest_group = min(
        baseline_metrics.group_metrics,
        key=lambda metric: metric.selection_rate,
    ).group
    disadvantaged_mask = groups == lowest_group
    reweighted_pred[disadvantaged_mask] = (scores[disadvantaged_mask] >= 0.43).astype(int)
    reweighted_metrics = compute_fairness_metrics(y_true, reweighted_pred, groups, positive_label)
    results.append(
        MitigationResult(
            strategy="Reweighting proxy simulation",
            accuracy=_accuracy(y_true, reweighted_pred),
            demographic_parity_difference=reweighted_metrics.demographic_parity_difference,
            equal_opportunity_difference=reweighted_metrics.equal_opportunity_difference,
            notes=f"Approximates giving more training weight to applicants in {lowest_group} by relaxing its score cutoff.",
        )
    )

    return results
