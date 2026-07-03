import io
import pickle

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from app.models.schemas import AuditRequest, AuditResponse, BenchmarkResponse
from app.services.audit_service import add_model_scores, audit_dataframe, load_sample_dataset
from app.services.benchmark_service import run_sample_benchmark

app = FastAPI(
    title="CivicPulse Fairness Audit API",
    description="Model-agnostic fairness auditing for public resource allocation.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/sample")
def sample_dataset() -> JSONResponse:
    df = load_sample_dataset()
    return JSONResponse(
        {
            "columns": list(df.columns),
            "rows": df.head(20).to_dict(orient="records"),
            "row_count": len(df),
        }
    )


@app.post("/audit", response_model=AuditResponse)
def run_audit(request: AuditRequest, persist: bool = False) -> AuditResponse:
    df = load_sample_dataset()
    return audit_dataframe(df, request, persist=persist)


@app.post("/audit/upload", response_model=AuditResponse)
async def run_uploaded_audit(
    file: UploadFile = File(...),
    target: str = "approved",
    protected_attribute: str = "district",
    score_column: str | None = "model_score",
    positive_label: int = 1,
) -> AuditResponse:
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a CSV file.")

    df = pd.read_csv(file.file)
    request = AuditRequest(
        target=target,
        protected_attribute=protected_attribute,
        score_column=score_column,
        positive_label=positive_label,
    )
    return audit_dataframe(df, request)


@app.post("/audit/model-upload", response_model=AuditResponse)
async def run_uploaded_model_audit(
    dataset: UploadFile = File(...),
    model_file: UploadFile = File(...),
    target: str = "approved",
    protected_attribute: str = "district",
    positive_label: int = 1,
) -> AuditResponse:
    if not dataset.filename or not dataset.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Dataset must be a CSV file.")
    if not model_file.filename or not model_file.filename.endswith((".pkl", ".pickle", ".joblib")):
        raise HTTPException(status_code=400, detail="Model must be a .pkl, .pickle, or .joblib file.")

    df = pd.read_csv(dataset.file)
    model_bytes = await model_file.read()
    try:
        if model_file.filename.endswith(".joblib"):
            import joblib

            model = joblib.load(io.BytesIO(model_bytes))
        else:
            model = pickle.loads(model_bytes)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to load model: {exc}") from exc

    try:
        scored_df = add_model_scores(df, model, target=target)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to score dataset with uploaded model: {exc}") from exc

    request = AuditRequest(
        target=target,
        protected_attribute=protected_attribute,
        score_column="model_score",
        positive_label=positive_label,
    )
    return audit_dataframe(scored_df, request)


@app.get("/benchmark/sample", response_model=BenchmarkResponse)
def sample_benchmark(
    target: str = "approved",
    protected_attribute: str = "district",
) -> BenchmarkResponse:
    return run_sample_benchmark(load_sample_dataset(), target=target, protected_attribute=protected_attribute)


@app.get("/exports/group-metrics.csv")
def export_group_metrics(protected_attribute: str = "district") -> StreamingResponse:
    audit = audit_dataframe(load_sample_dataset(), AuditRequest(protected_attribute=protected_attribute))
    rows = [
        {
            "audit_id": audit.audit_id,
            "protected_attribute": audit.protected_attribute,
            **metric.model_dump(),
        }
        for metric in audit.metrics.group_metrics
    ]
    csv_body = pd.DataFrame(rows).to_csv(index=False)
    return StreamingResponse(
        iter([csv_body]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=group_metrics.csv"},
    )


@app.get("/exports/mitigation-results.csv")
def export_mitigation_results(protected_attribute: str = "district") -> StreamingResponse:
    audit = audit_dataframe(load_sample_dataset(), AuditRequest(protected_attribute=protected_attribute))
    rows = [
        {
            "audit_id": audit.audit_id,
            "protected_attribute": audit.protected_attribute,
            **result.model_dump(),
        }
        for result in audit.mitigation
    ]
    csv_body = pd.DataFrame(rows).to_csv(index=False)
    return StreamingResponse(
        iter([csv_body]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=mitigation_results.csv"},
    )
