import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from app.models.schemas import ExplanationItem


EXCLUDED_COLUMNS = {"approved", "prediction", "model_score", "applicant_id"}


def _numeric_feature_columns(df: pd.DataFrame, target: str) -> list[str]:
    return [
        col
        for col in df.select_dtypes(include="number").columns
        if col not in EXCLUDED_COLUMNS and col != target
    ]


def _explain_with_shap_and_lime(df: pd.DataFrame, target: str) -> list[ExplanationItem]:
    import numpy as np
    import shap
    from lime.lime_tabular import LimeTabularExplainer

    feature_cols = _numeric_feature_columns(df, target)
    if len(feature_cols) < 2 or df[target].nunique() < 2:
        return []

    x = df[feature_cols].astype(float)
    y = df[target].astype(int)
    x_train, x_test, y_train, _ = train_test_split(x, y, test_size=0.35, random_state=42, stratify=y)
    model = RandomForestClassifier(n_estimators=80, max_depth=4, random_state=42)
    model.fit(x_train.to_numpy(), y_train)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(x_test.to_numpy())
    class_one_values = shap_values[:, :, 1] if isinstance(shap_values, np.ndarray) and shap_values.ndim == 3 else shap_values[1]
    shap_importance = np.abs(class_one_values).mean(axis=0)

    lime_explainer = LimeTabularExplainer(
        training_data=x_train.to_numpy(),
        feature_names=feature_cols,
        class_names=["denied", "approved"],
        mode="classification",
        discretize_continuous=True,
    )
    lime_exp = lime_explainer.explain_instance(
        x_test.iloc[0].to_numpy(),
        model.predict_proba,
        num_features=min(6, len(feature_cols)),
    )
    lime_weights = dict(lime_exp.as_list())

    items: list[ExplanationItem] = []
    for feature, impact in sorted(
        zip(feature_cols, shap_importance, strict=True),
        key=lambda pair: float(pair[1]),
        reverse=True,
    )[:6]:
        matching_lime = next((weight for label, weight in lime_weights.items() if feature in label), 0.0)
        direction = "increases approval likelihood" if matching_lime >= 0 else "decreases approval likelihood"
        items.append(
            ExplanationItem(
                feature=feature,
                impact=round(float(impact), 4),
                direction=f"SHAP ranks this as influential; LIME says it {direction} for a representative case.",
            )
        )
    return items


def explain_feature_gaps(
    df: pd.DataFrame,
    target: str,
    protected_attribute: str,
    score_column: str | None,
) -> list[ExplanationItem]:
    """Explain audit drivers with SHAP/LIME and fall back to feature gaps."""
    try:
        shap_lime_items = _explain_with_shap_and_lime(df, target)
        if shap_lime_items:
            return shap_lime_items
    except Exception:
        pass

    score = score_column if score_column in df.columns else target
    rates = df.groupby(protected_attribute)[score].mean().sort_values()
    if len(rates) < 2:
        return []

    low_group = rates.index[0]
    high_group = rates.index[-1]
    numeric_cols = _numeric_feature_columns(df, target)

    items: list[ExplanationItem] = []
    for col in numeric_cols:
        low_mean = float(df.loc[df[protected_attribute] == low_group, col].mean())
        high_mean = float(df.loc[df[protected_attribute] == high_group, col].mean())
        impact = high_mean - low_mean
        items.append(
            ExplanationItem(
                feature=col,
                impact=round(abs(impact), 4),
                direction=f"{high_group} has {'higher' if impact >= 0 else 'lower'} average {col} than {low_group}",
            )
        )

    return sorted(items, key=lambda item: item.impact, reverse=True)[:6]
