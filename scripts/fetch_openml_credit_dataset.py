from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.datasets import fetch_openml


OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "public_credit_fairness.csv"


def main() -> None:
    dataset = fetch_openml(name="credit-g", version=1, as_frame=True)
    df = dataset.frame.copy()
    if "class" not in df.columns:
        raise ValueError("OpenML credit-g dataset did not include the expected class column.")

    normalized = pd.DataFrame(
        {
            "applicant_id": range(1, len(df) + 1),
            "district": df["foreign_worker"].astype(str),
            "income_band": df["checking_status"].astype(str),
            "age_band": pd.cut(
                df["age"].astype(float),
                bins=[0, 24, 44, 64, 120],
                labels=["18-24", "25-44", "45-64", "65+"],
                include_lowest=True,
            ).astype(str),
            "household_size": df["num_dependents"].astype(int),
            "prior_eviction": (df["credit_history"].astype(str) == "critical/other existing credit").astype(int),
            "monthly_income": df["credit_amount"].astype(float),
            "rent_burden": df["duration"].astype(float) / df["duration"].astype(float).max(),
            "years_in_city": df["residence_since"].astype(float),
            "caseworker_score": df["employment"].astype(str).astype("category").cat.codes + 60,
            "model_score": (df["class"].astype(str) == "good").astype(float),
            "approved": (df["class"].astype(str) == "good").astype(int),
        }
    )
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    normalized.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {OUTPUT_PATH} with {len(normalized)} rows.")


if __name__ == "__main__":
    main()
