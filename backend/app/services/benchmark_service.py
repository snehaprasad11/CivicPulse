import numpy as np
import pandas as pd
import torch
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

from app.core.fairness_metrics import compute_fairness_metrics
from app.ml.adversarial_debiasing import train_adversarial_model
from app.models.schemas import BenchmarkMetric, BenchmarkResponse


def _preprocessor(df: pd.DataFrame, target: str, protected_attribute: str) -> ColumnTransformer:
    feature_df = df.drop(columns=[target, protected_attribute])
    numeric = list(feature_df.select_dtypes(include="number").columns)
    categorical = [col for col in feature_df.columns if col not in numeric]
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ]
    )


def _metric_row(
    model_name: str,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    groups: np.ndarray,
    notes: str,
) -> BenchmarkMetric:
    fairness = compute_fairness_metrics(y_true, y_pred, groups)
    return BenchmarkMetric(
        model_name=model_name,
        accuracy=float(accuracy_score(y_true, y_pred)),
        disparate_impact_ratio=fairness.disparate_impact_ratio,
        demographic_parity_difference=fairness.demographic_parity_difference,
        equal_opportunity_difference=fairness.equal_opportunity_difference,
        notes=notes,
    )


def run_sample_benchmark(
    df: pd.DataFrame,
    target: str = "approved",
    protected_attribute: str = "district",
) -> BenchmarkResponse:
    x = df.drop(columns=[target])
    y = df[target].astype(int)
    groups = df[protected_attribute].astype(str)

    x_train, x_test, y_train, y_test, groups_train, groups_test = train_test_split(
        x,
        y,
        groups,
        test_size=0.35,
        random_state=42,
        stratify=y,
    )

    preprocess = _preprocessor(df, target, protected_attribute)
    train_features = x_train.drop(columns=[protected_attribute])
    test_features = x_test.drop(columns=[protected_attribute])

    logistic = Pipeline(
        steps=[
            ("preprocess", preprocess),
            ("classifier", LogisticRegression(max_iter=1000, solver="liblinear")),
        ]
    )
    logistic.fit(train_features, y_train)
    logistic_pred = logistic.predict(test_features)

    xgb_preprocess = _preprocessor(df, target, protected_attribute)
    xgb_train = xgb_preprocess.fit_transform(train_features)
    xgb_test = xgb_preprocess.transform(test_features)
    xgboost = XGBClassifier(
        n_estimators=80,
        max_depth=3,
        learning_rate=0.08,
        eval_metric="logloss",
        random_state=42,
    )
    xgboost.fit(xgb_train, y_train)
    xgb_pred = xgboost.predict(xgb_test)

    encoded_train = logistic.named_steps["preprocess"].transform(train_features)
    encoded_test = logistic.named_steps["preprocess"].transform(test_features)
    if hasattr(encoded_train, "toarray"):
        encoded_train = encoded_train.toarray()
        encoded_test = encoded_test.toarray()

    protected_codes, uniques = pd.factorize(groups_train)
    adversarial = train_adversarial_model(
        x=torch.tensor(encoded_train, dtype=torch.float32),
        y=torch.tensor(y_train.to_numpy(), dtype=torch.float32),
        protected=torch.tensor(protected_codes, dtype=torch.long),
        protected_classes=len(uniques),
        epochs=35,
        lambda_=0.9,
    )
    adversarial.eval()
    with torch.no_grad():
        logits, _ = adversarial(torch.tensor(encoded_test, dtype=torch.float32), lambda_=0.0)
        adv_pred = (torch.sigmoid(logits).numpy() >= 0.5).astype(int)

    return BenchmarkResponse(
        dataset_rows=len(df),
        protected_attribute=protected_attribute,
        target=target,
        results=[
            _metric_row(
                "Logistic regression",
                y_test.to_numpy(),
                logistic_pred,
                groups_test.to_numpy(),
                "Transparent linear baseline for policy review.",
            ),
            _metric_row(
                "XGBoost",
                y_test.to_numpy(),
                xgb_pred,
                groups_test.to_numpy(),
                "High-performing tree ensemble baseline.",
            ),
            _metric_row(
                "PyTorch adversarial debiasing",
                y_test.to_numpy(),
                adv_pred,
                groups_test.to_numpy(),
                "Neural network trained with a protected-attribute adversary.",
            ),
        ],
    )
