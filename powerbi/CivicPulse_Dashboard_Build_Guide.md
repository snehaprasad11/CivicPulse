# CivicPulse Power BI Dashboard Build Guide

This is the exact recipe to create the real Power BI `.pbix` dashboard from the CivicPulse API exports.

## Data Sources

Use Power BI Desktop > Get Data > Web:

```text
http://127.0.0.1:8000/exports/group-metrics.csv
http://127.0.0.1:8000/exports/mitigation-results.csv
```

For an offline demo, use:

```text
powerbi/group_metrics_sample.csv
powerbi/mitigation_results_sample.csv
```

Rename the imported tables:

- `group_metrics`
- `mitigation_results`

## Relationships

Create a relationship:

```text
group_metrics[protected_attribute] 1:* mitigation_results[protected_attribute]
```

Set cross-filter direction to single.

## Dashboard Page 1: City Fairness Overview

Canvas: 16:9.

Visuals:

- KPI card: `Disparate Impact Ratio`
- KPI card: `Demographic Parity Gap`
- KPI card: `Equal Opportunity Gap`
- Clustered column chart: `selection_rate` and `accuracy` by `group`
- Table: group, count, selection rate, TPR, FPR, accuracy
- Slicer: protected_attribute

## Dashboard Page 2: Mitigation Comparison

Visuals:

- Matrix: strategy by accuracy, demographic parity difference, equal opportunity difference
- Bar chart: demographic parity difference by strategy
- Bar chart: accuracy by strategy
- Text table: mitigation notes

## Dashboard Page 3: Analyst Brief

Visuals:

- KPI card: lowest selection rate
- KPI card: highest selection rate
- KPI card: adverse impact flag
- Table: group metrics sorted by selection rate
- Text box: policy interpretation and caveats

## Export

After building the report:

1. Save as `powerbi/CivicPulse_Fairness_Dashboard.pbix`.
2. Export PDF screenshots for your presentation.
3. Publish to Power BI Service if using a school or organization account.
