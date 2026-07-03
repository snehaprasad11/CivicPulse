# API

Base URL in local development: `http://localhost:8000`

## `GET /health`

Returns backend health.

## `GET /sample`

Returns the sample dataset metadata and first 20 rows.

## `POST /audit`

Runs an audit on the bundled sample dataset.

```json
{
  "target": "approved",
  "protected_attribute": "district",
  "score_column": "model_score",
  "positive_label": 1,
  "threshold": 0.5
}
```

## `POST /audit/upload`

Runs an audit on an uploaded CSV.

Multipart form fields:

- `file`: CSV file
- `target`: target label column
- `protected_attribute`: group column to audit
- `score_column`: model score column
- `positive_label`: positive decision label

## `POST /audit/model-upload`

Runs an audit using an uploaded CSV and serialized model.

Multipart form fields:

- `dataset`: CSV file
- `model_file`: `.pkl`, `.pickle`, or `.joblib` model
- `target`: target label column
- `protected_attribute`: group column to audit
- `positive_label`: positive decision label

The model must expose `predict_proba`, `decision_function`, or `predict`.

## `GET /benchmark/sample`

Compares logistic regression, XGBoost, and PyTorch adversarial debiasing on the sample dataset.

## `GET /exports/group-metrics.csv`

Exports group-level fairness metrics for Power BI.

## `GET /exports/mitigation-results.csv`

Exports mitigation simulation rows for Power BI.
