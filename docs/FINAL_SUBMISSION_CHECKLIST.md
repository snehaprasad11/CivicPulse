# Final Submission Checklist

## Completed

- Full-stack React + FastAPI app
- Custom fairness metrics from scratch
- SHAP and LIME explanation path
- PyTorch adversarial debiasing architecture
- Logistic regression and XGBoost benchmark endpoint
- CSV upload workflow
- Serialized `.pkl`, `.pickle`, and `.joblib` model-upload workflow
- Power BI CSV export endpoints and sample CSVs
- Power BI build guide, DAX measures, Power Query scripts, and layout spec
- Supabase schema and persistence hook
- Ollama summary hook with deterministic fallback
- GitHub Actions CI for backend and frontend
- Demo scenario and generated MP4 walkthrough
- Render and Vercel deployment configuration

## Ready But Requires Account Credentials

- Render deployment: requires logging into Render and creating a web service from `render.yaml`.
- Vercel deployment: requires Vercel login and `VITE_API_URL` pointing to the Render API.
- Supabase persistence: requires a Supabase project URL and service-role key.
- Ollama summary generation in production: requires an Ollama host or compatible local LLM endpoint.
- Final `.pbix` export: requires opening Power BI Desktop and saving the report after applying `powerbi/CivicPulse_Dashboard_Build_Guide.md`.

## Recommended Submission Order

1. Push latest `master` to GitHub.
2. Confirm GitHub Actions is green.
3. Deploy backend on Render.
4. Deploy frontend on Vercel with `VITE_API_URL`.
5. Run `docs/SUPABASE_SCHEMA.sql` in Supabase and add backend env vars.
6. Publish `notebooks/civicpulse_kaggle_starter.ipynb` with a public dataset result.
7. Include `demo/civicpulse_demo.mp4` in the project presentation.
