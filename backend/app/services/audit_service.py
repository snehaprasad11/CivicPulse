from pathlib import Path
from uuid import uuid4

import numpy as np
import pandas as pd

from app.core.explainability import explain_feature_gaps
from app.core.fairness_metrics import compute_fairness_metrics
from app.core.mitigation import simulate_threshold_mitigation
from app.core.summary import build_plain_english_summary
from app.db.supabase import save_audit_run
from app.models.schemas import AuditRequest, AuditResponse

DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "sample_housing_assistance.csv"


def load_sample_dataset() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def predictions_from_request(df: pd.DataFrame, request: AuditRequest) -> np.ndarray:
    if request.score_column and request.score_column in df.columns:
        return (df[request.score_column].astype(float).to_numpy() >= request.threshold).astype(int)
    if "prediction" in df.columns:
        return df["prediction"].astype(int).to_numpy()
    return df[request.target].astype(int).to_numpy()


def add_model_scores(
    df: pd.DataFrame,
    model,
    target: str,
    score_column: str = "model_score",
) -> pd.DataFrame:
    feature_df = df.drop(columns=[target])
    scored_df = df.copy()
    if hasattr(model, "predict_proba"):
        scored_df[score_column] = model.predict_proba(feature_df)[:, 1]
    elif hasattr(model, "decision_function"):
        raw_scores = model.decision_function(feature_df)
        scored_df[score_column] = 1 / (1 + np.exp(-raw_scores))
    elif hasattr(model, "predict"):
        scored_df["prediction"] = model.predict(feature_df).astype(int)
    else:
        raise ValueError("Model must expose predict, predict_proba, or decision_function.")
    return scored_df


def audit_dataframe(df: pd.DataFrame, request: AuditRequest, persist: bool = False) -> AuditResponse:
    required = {request.target, request.protected_attribute}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    y_true = df[request.target].astype(int).to_numpy()
    y_pred = predictions_from_request(df, request)
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

    audit_id = str(uuid4())
    response = AuditResponse(
        audit_id=audit_id,
        dataset_rows=len(df),
        protected_attribute=request.protected_attribute,
        target=request.target,
        metrics=metrics,
        mitigation=mitigation,
        explanations=explanations,
        plain_english_summary=summary,
    )

    if persist:
        response.persisted = save_audit_run(
            {
                "id": audit_id,
                "protected_attribute": request.protected_attribute,
                "target": request.target,
                "dataset_rows": len(df),
                "summary": summary,
                "metrics": metrics.model_dump(),
                "mitigation": [item.model_dump() for item in mitigation],
                "explanations": [item.model_dump() for item in explanations],
            }
        )

    return response
