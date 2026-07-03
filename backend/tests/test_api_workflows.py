from fastapi.testclient import TestClient
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.main import app
from app.services.audit_service import load_sample_dataset


client = TestClient(app)


def test_sample_audit_endpoint_returns_report() -> None:
    response = client.post("/audit", json={"protected_attribute": "district"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["dataset_rows"] == 24
    assert payload["metrics"]["disparate_impact_ratio"] < 0.8
    assert payload["explanations"]


def test_powerbi_group_metrics_export() -> None:
    response = client.get("/exports/group-metrics.csv")

    assert response.status_code == 200
    assert "group,count,selection_rate" in response.text
    assert "South,6,0.3333333333333333" in response.text


def test_csv_upload_respects_form_fields() -> None:
    csv_bytes = load_sample_dataset().to_csv(index=False).encode()

    response = client.post(
        "/audit/upload",
        files={"file": ("sample.csv", csv_bytes, "text/csv")},
        data={
            "target": "approved",
            "protected_attribute": "income_band",
            "score_column": "model_score",
        },
    )

    assert response.status_code == 200
    assert response.json()["protected_attribute"] == "income_band"


def test_model_upload_endpoint_scores_serialized_model() -> None:
    import pickle

    df = load_sample_dataset()
    x = df.drop(columns=["approved"])
    y = df["approved"]
    numeric = list(x.select_dtypes(include="number").columns)
    categorical = [col for col in x.columns if col not in numeric]
    model = Pipeline(
        steps=[
            (
                "preprocess",
                ColumnTransformer(
                    transformers=[
                        ("num", StandardScaler(), numeric),
                        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
                    ]
                ),
            ),
            ("classifier", LogisticRegression(max_iter=1000, solver="liblinear")),
        ]
    )
    model.fit(x, y)

    response = client.post(
        "/audit/model-upload",
        files={
            "dataset": ("sample.csv", df.to_csv(index=False).encode(), "text/csv"),
            "model_file": ("model.pkl", pickle.dumps(model), "application/octet-stream"),
        },
        data={"target": "approved", "protected_attribute": "district"},
    )

    assert response.status_code == 200
    assert response.json()["dataset_rows"] == 24


def test_sample_benchmark_endpoint_compares_core_models() -> None:
    response = client.get("/benchmark/sample")

    assert response.status_code == 200
    model_names = {item["model_name"] for item in response.json()["results"]}
    assert model_names == {
        "Logistic regression",
        "XGBoost",
        "PyTorch adversarial debiasing",
    }
