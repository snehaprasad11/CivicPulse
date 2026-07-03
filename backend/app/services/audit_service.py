from pathlib import Path

import numpy as np
import pandas as pd

from app.core.explainability import explain_feature_gaps
from app.core.fairness_metrics import compute_fairness_metrics
from app.core.mitigation import simulate_threshold_mitigation
from app.core.summary import build_plain_english_summary
from app.models.schemas import AuditRequest, AuditResponse

DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "sample_housing_assistance.csv"


def load_sample_dataset() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def _predictions_from_request(df: pd.DataFrame, request: AuditRequest) -> np.ndarray:
    if request.score_column and request.score_column in df.columns:
        return (df[request.score_column].astype(float).to_numpy() >= request.threshold).astype(int)
    if "prediction" in df.columns:
        return df["prediction"].astype(int).to_numpy()
    return df[request.target].astype(int).to_numpy()


def audit_dataframe(df: pd.DataFrame, request: AuditRequest) -> AuditResponse:
    required = {request.target, request.protected_attribute}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    y_true = df[request.target].astype(int).to_numpy()
    y_pred = _predictions_from_request(df, request)
    groups = df[request.protected_attribute].astype(str).to_numpy()

    metrics = compute_fairness_metrics(
        y_true=y_true,
        y_pred=y_pred,
        groups=groups,
        positive_label=request.positive_label,
    )

    mitigation = simulate_threshold_mitigation(
        df=df,
        target=request.target,
        protected_attribute=request.protected_attribute,
        score_column=request.score_column,
        positive_label=request.positive_label,
    )

    explanations = explain_feature_gaps(
        df=df,
        target=request.target,
        protected_attribute=request.protected_attribute,
        score_column=request.score_column,
    )

    summary = build_plain_english_summary(
        protected_attribute=request.protected_attribute,
        metrics=metrics,
        explanations=explanations,
    )

    return AuditResponse(
        dataset_rows=len(df),
        protected_attribute=request.protected_attribute,
        target=request.target,
        metrics=metrics,
        mitigation=mitigation,
        explanations=explanations,
        plain_english_summary=summary,
    )
