from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.main import app  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    output_dir = ROOT / "docs" / "proofs"
    output_dir.mkdir(parents=True, exist_ok=True)

    client = TestClient(app)
    generated_at = datetime.now(UTC).isoformat()

    health = client.get("/health")
    health.raise_for_status()
    write_json(
        output_dir / "health.json",
        {
            "generated_at": generated_at,
            "endpoint": "GET /health",
            "status_code": health.status_code,
            "response": health.json(),
        },
    )

    audit = client.post("/audit", json={"protected_attribute": "district"})
    audit.raise_for_status()
    audit_payload = audit.json()
    write_json(
        output_dir / "sample_audit_district.json",
        {
            "generated_at": generated_at,
            "endpoint": "POST /audit",
            "request": {"protected_attribute": "district"},
            "response": audit_payload,
        },
    )

    benchmark = client.get("/benchmark/sample")
    benchmark.raise_for_status()
    write_json(
        output_dir / "sample_benchmark.json",
        {
            "generated_at": generated_at,
            "endpoint": "GET /benchmark/sample",
            "response": benchmark.json(),
        },
    )

    group_metrics = client.get("/exports/group-metrics.csv")
    group_metrics.raise_for_status()
    (output_dir / "group_metrics_export.csv").write_text(group_metrics.text, encoding="utf-8")

    mitigation = client.get("/exports/mitigation-results.csv")
    mitigation.raise_for_status()
    (output_dir / "mitigation_results_export.csv").write_text(mitigation.text, encoding="utf-8")

    summary = {
        "generated_at": generated_at,
        "dataset_rows": audit_payload["dataset_rows"],
        "protected_attribute": audit_payload["protected_attribute"],
        "disparate_impact_ratio": audit_payload["metrics"]["disparate_impact_ratio"],
        "demographic_parity_difference": audit_payload["metrics"]["demographic_parity_difference"],
        "equal_opportunity_difference": audit_payload["metrics"]["equal_opportunity_difference"],
        "benchmark_models": [item["model_name"] for item in benchmark.json()["results"]],
        "plain_english_summary": audit_payload["plain_english_summary"],
        "proof_files": [
            "health.json",
            "sample_audit_district.json",
            "sample_benchmark.json",
            "group_metrics_export.csv",
            "mitigation_results_export.csv",
        ],
    }
    write_json(output_dir / "proof_summary.json", summary)

    print(f"Wrote proof artifacts to {output_dir}")


if __name__ == "__main__":
    main()
