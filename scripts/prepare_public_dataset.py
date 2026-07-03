from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def normalize_dataset(
    input_path: Path,
    output_path: Path,
    target: str,
    protected_attribute: str,
    score_column: str | None,
) -> None:
    df = pd.read_csv(input_path)
    required = {target, protected_attribute}
    if score_column:
        required.add(score_column)
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in source dataset: {', '.join(sorted(missing))}")

    normalized = df.copy()
    if target != "approved":
        normalized["approved"] = normalized[target].astype(int)
    if protected_attribute != "district":
        normalized["district"] = normalized[protected_attribute].astype(str)
    if score_column and score_column != "model_score":
        normalized["model_score"] = normalized[score_column].astype(float)

    if "model_score" not in normalized.columns:
        normalized["model_score"] = normalized["approved"].astype(float)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    normalized.to_csv(output_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize a public allocation dataset for CivicPulse.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", default=Path("data/public_resource_allocation.csv"), type=Path)
    parser.add_argument("--target", required=True)
    parser.add_argument("--protected-attribute", required=True)
    parser.add_argument("--score-column")
    args = parser.parse_args()

    normalize_dataset(
        input_path=args.input,
        output_path=args.output,
        target=args.target,
        protected_attribute=args.protected_attribute,
        score_column=args.score_column,
    )


if __name__ == "__main__":
    main()
