from pydantic import BaseModel, Field


class AuditRequest(BaseModel):
    target: str = Field(default="approved")
    protected_attribute: str = Field(default="district")
    score_column: str | None = Field(default="model_score")
    positive_label: int = Field(default=1)
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)


class GroupMetric(BaseModel):
    group: str
    count: int
    selection_rate: float
    true_positive_rate: float | None
    false_positive_rate: float | None
    accuracy: float | None


class FairnessMetrics(BaseModel):
    reference_group: str
    disparate_impact_ratio: float | None
    demographic_parity_difference: float
    equal_opportunity_difference: float | None
    equalized_odds_difference: float | None
    group_metrics: list[GroupMetric]


class MitigationResult(BaseModel):
    strategy: str
    accuracy: float | None
    demographic_parity_difference: float
    equal_opportunity_difference: float | None
    notes: str


class ExplanationItem(BaseModel):
    feature: str
    impact: float
    direction: str


class AuditResponse(BaseModel):
    dataset_rows: int
    protected_attribute: str
    target: str
    metrics: FairnessMetrics
    mitigation: list[MitigationResult]
    explanations: list[ExplanationItem]
    plain_english_summary: str
