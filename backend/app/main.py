from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models.schemas import AuditRequest, AuditResponse
from app.services.audit_service import audit_dataframe, load_sample_dataset

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
def run_audit(request: AuditRequest) -> AuditResponse:
    df = load_sample_dataset()
    return audit_dataframe(df, request)


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

    import pandas as pd

    df = pd.read_csv(file.file)
    request = AuditRequest(
        target=target,
        protected_attribute=protected_attribute,
        score_column=score_column,
        positive_label=positive_label,
    )
    return audit_dataframe(df, request)
