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
