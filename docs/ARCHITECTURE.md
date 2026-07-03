# CivicPulse Architecture

## Data Flow

1. A user selects a protected attribute or uploads a CSV.
2. FastAPI validates the dataset and creates model predictions from a score column or prediction column.
3. The fairness core computes group metrics from first principles.
4. The mitigation module simulates threshold and reweighting strategies.
5. The explanation module ranks feature gaps and can be replaced with SHAP/LIME when a serialized model is provided.
6. The frontend renders a policy-analyst-friendly report.
7. Optional Supabase persistence stores audit runs as JSONB.
8. Power BI endpoints export group metrics and mitigation comparisons as CSV.

## Core Services

- `backend/app/core/fairness_metrics.py`: custom fairness metrics.
- `backend/app/core/mitigation.py`: simulation layer for fairness/accuracy trade-offs.
- `backend/app/core/explainability.py`: explanation fallback and SHAP/LIME extension point.
- `backend/app/ml/adversarial_debiasing.py`: PyTorch adversarial debiasing model.
- `backend/app/services/benchmark_service.py`: logistic regression, XGBoost, and adversarial model comparison.
- `backend/app/db/supabase.py`: optional Supabase REST persistence.

## Deployment Target

- Frontend: Vercel
- Backend: Render
- Database and artifact storage: Supabase
- Local LLM summaries: Ollama integration can be added behind the summary service.

## Next Production Steps

- Add authenticated project workspaces.
- Store audit runs and uploaded datasets in Supabase.
- Add serialized model upload support for scikit-learn, XGBoost, and PyTorch.
- Add a background worker for expensive SHAP runs.
- Add Power BI dataset refresh automation.
