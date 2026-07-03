# Proof Artifacts

These files are generated from the FastAPI app, so reviewers can inspect concrete outputs without starting the UI.

Regenerate them with:

```bash
python scripts/generate_proof_artifacts.py
```

## Files

- `health.json`: health-check proof from `GET /health`.
- `sample_audit_district.json`: full district-level fairness audit from `POST /audit`.
- `sample_benchmark.json`: logistic regression, XGBoost, and PyTorch adversarial-debiasing comparison.
- `group_metrics_export.csv`: Power BI-ready group metrics export.
- `mitigation_results_export.csv`: Power BI-ready mitigation comparison export.
- `proof_summary.json`: small evaluator-friendly summary of the generated proof snapshot.
