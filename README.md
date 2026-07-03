# CivicPulse

Algorithmic fairness auditing for public resource allocation decisions.

CivicPulse is a full-stack, model-agnostic auditing platform for policy analysts, NGOs, and city teams who need to inspect whether an eligibility or prioritization model treats protected groups differently. It combines custom fairness metric implementations, explainability, mitigation simulation, and a deep adversarial debiasing baseline.

## What It Does

- Upload or use a sample civic resource-allocation dataset.
- Upload a trained `.pkl`, `.pickle`, or `.joblib` model through the API.
- Audit fairness across protected attributes such as district, age band, and income band.
- Compute fairness metrics from scratch:
  - Disparate impact ratio
  - Demographic parity difference
  - Equal opportunity difference
  - Equalized odds difference
- Show model performance and group-level approval/denial patterns.
- Generate plain-English summaries for non-technical stakeholders.
- Simulate mitigation strategies:
  - Group threshold adjustment
  - Instance reweighting
  - Adversarial debiasing neural network reference implementation
- Export city-dashboard-ready CSV files for Power BI.
- Compare logistic regression, XGBoost, and PyTorch adversarial-debiasing baselines.

## Repo Layout

```text
backend/      FastAPI service and ML fairness core
frontend/     React + Tailwind PWA dashboard
data/         Sample public-resource allocation dataset
docs/         Architecture, API, and resume/Kaggle notes
notebooks/    Kaggle notebook starter
powerbi/      Power BI dashboard schema and exported metrics
```

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the API at `http://localhost:8000`.

## Main API Endpoints

- `POST /audit`: audit the bundled sample dataset.
- `POST /audit/upload`: audit an uploaded CSV.
- `POST /audit/model-upload`: audit an uploaded CSV with an uploaded model artifact.
- `GET /benchmark/sample`: compare logistic regression, XGBoost, and PyTorch adversarial debiasing.
- `GET /exports/group-metrics.csv`: export Power BI-ready group metrics.
- `GET /exports/mitigation-results.csv`: export Power BI-ready mitigation results.

## Sample Dataset

The included sample dataset is synthetic, but shaped like a housing-assistance prioritization workflow. It is useful for demos, tests, and development without exposing real applicant data.

For a publishable Kaggle version, replace it with a public dataset such as HMDA mortgage data or an open housing-assistance dataset and keep the same audit pipeline.

Use `scripts/prepare_public_dataset.py` to normalize a public CSV into the columns CivicPulse expects.

## Resume Line

Built a model-agnostic algorithmic fairness auditing platform combining custom fairness-metric implementations, SHAP-based explainability, and an adversarial-debiasing neural network, enabling non-technical stakeholders to detect and mitigate bias in public resource-allocation models via an interactive web app.
