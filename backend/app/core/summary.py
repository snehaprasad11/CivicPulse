import os

import httpx

from app.models.schemas import ExplanationItem, FairnessMetrics


def _fallback_summary(
    protected_attribute: str,
    metrics: FairnessMetrics,
    explanations: list[ExplanationItem],
) -> str:
    lowest = min(metrics.group_metrics, key=lambda metric: metric.selection_rate)
    highest = max(metrics.group_metrics, key=lambda metric: metric.selection_rate)
    ratio = metrics.disparate_impact_ratio
    ratio_text = "not available" if ratio is None else f"{ratio:.2f}"
    top_driver = explanations[0].feature if explanations else "the available input features"

    return (
        f"Across {protected_attribute}, {highest.group} receives the highest positive decision rate "
        f"({highest.selection_rate:.1%}) while {lowest.group} receives the lowest "
        f"({lowest.selection_rate:.1%}). The disparate impact ratio is {ratio_text}; values below "
        f"0.80 are commonly treated as a warning sign for adverse impact. The largest observed "
        f"feature gap is {top_driver}, so analysts should inspect whether that feature is a valid "
        f"policy criterion or a proxy for neighborhood disadvantage."
    )


def build_plain_english_summary(
    protected_attribute: str,
    metrics: FairnessMetrics,
    explanations: list[ExplanationItem],
) -> str:
    fallback = _fallback_summary(protected_attribute, metrics, explanations)
    ollama_url = os.getenv("OLLAMA_URL")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1")
    if not ollama_url:
        return fallback

    prompt = (
        "Write a concise, plain-English fairness audit finding for a city policy analyst. "
        "Avoid legal conclusions. Use these metrics and feature signals:\n"
        f"Protected attribute: {protected_attribute}\n"
        f"Reference group: {metrics.reference_group}\n"
        f"Disparate impact ratio: {metrics.disparate_impact_ratio}\n"
        f"Demographic parity difference: {metrics.demographic_parity_difference}\n"
        f"Equal opportunity difference: {metrics.equal_opportunity_difference}\n"
        f"Groups: {[metric.model_dump() for metric in metrics.group_metrics]}\n"
        f"Feature signals: {[item.model_dump() for item in explanations[:4]]}"
    )

    try:
        response = httpx.post(
            f"{ollama_url.rstrip('/')}/api/generate",
            json={"model": ollama_model, "prompt": prompt, "stream": False},
            timeout=8,
        )
        response.raise_for_status()
        generated = response.json().get("response", "").strip()
        return generated or fallback
    except Exception:
        return fallback
