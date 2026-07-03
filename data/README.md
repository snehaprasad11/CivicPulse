# Data

`sample_housing_assistance.csv` is synthetic demo data shaped like a housing-assistance prioritization workflow.

For final publication, normalize a real public dataset into the same expected columns:

- `approved`: binary target where `1` is the beneficial outcome
- `model_score`: model probability or score, from `0` to `1`
- `district`: default protected/grouping column for demos

Example:

```bash
python scripts/prepare_public_dataset.py \
  --input raw_public_dataset.csv \
  --output data/public_resource_allocation.csv \
  --target approved_column \
  --protected-attribute district_column \
  --score-column probability_column
```
