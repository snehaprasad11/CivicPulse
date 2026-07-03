# Power BI Dashboard Schema

Use the API response or exported CSVs to build these visuals.

## Tables

### `group_metrics`

- `protected_attribute`
- `group`
- `count`
- `selection_rate`
- `true_positive_rate`
- `false_positive_rate`
- `accuracy`

### `mitigation_results`

- `strategy`
- `accuracy`
- `demographic_parity_difference`
- `equal_opportunity_difference`
- `notes`

## Recommended Visuals

- Clustered bar chart: selection rate by group
- KPI card: disparate impact ratio
- KPI card: demographic parity difference
- Matrix: before/after mitigation comparison
- Slicer: protected attribute
- Text box: plain-English finding

## Included Samples

- `group_metrics_sample.csv`
- `mitigation_results_sample.csv`

In Power BI, import both CSVs and relate them on `protected_attribute`. For live dashboards, use the backend export URLs as web data sources.
