from fastapi.testclient import TestClient

from app.main import app


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


def test_sample_benchmark_endpoint_compares_core_models() -> None:
    response = client.get("/benchmark/sample")

    assert response.status_code == 200
    model_names = {item["model_name"] for item in response.json()["results"]}
    assert model_names == {
        "Logistic regression",
        "XGBoost",
        "PyTorch adversarial debiasing",
    }
