from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier


def build_preprocessor(df: pd.DataFrame, target: str) -> ColumnTransformer:
    feature_df = df.drop(columns=[target])
    numeric = list(feature_df.select_dtypes(include="number").columns)
    categorical = [col for col in feature_df.columns if col not in numeric]
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ]
    )


def train_logistic_baseline(df: pd.DataFrame, target: str) -> Pipeline:
    model = Pipeline(
        steps=[
            ("preprocess", build_preprocessor(df, target)),
            ("classifier", LogisticRegression(max_iter=1000, solver="liblinear")),
        ]
    )
    return model.fit(df.drop(columns=[target]), df[target])


def train_xgboost_baseline(df: pd.DataFrame, target: str) -> Pipeline:
    model = Pipeline(
        steps=[
            ("preprocess", build_preprocessor(df, target)),
            (
                "classifier",
                XGBClassifier(
                    n_estimators=100,
                    max_depth=3,
                    learning_rate=0.08,
                    eval_metric="logloss",
                    random_state=42,
                ),
            ),
        ]
    )
    return model.fit(df.drop(columns=[target]), df[target])


def evaluate_binary_classifier(model: Pipeline, x: pd.DataFrame, y: pd.Series) -> dict[str, float]:
    probabilities = model.predict_proba(x)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    return {
        "accuracy": float(accuracy_score(y, predictions)),
        "roc_auc": float(roc_auc_score(y, probabilities)),
    }
