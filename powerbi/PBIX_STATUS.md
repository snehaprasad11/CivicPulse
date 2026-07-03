# CivicPulse PBIX Status

Target PBIX path:

```text
powerbi/CivicPulse_Fairness_Dashboard.pbix
```

## Current Status

The Power BI build kit is present in this repository, but a valid `.pbix` file must be saved from Power BI Desktop. A `.pbix` is a proprietary Power BI Desktop report package, so this repo should not include a fake renamed archive or an unrelated report.

## Build Kit Already Included

- `group_metrics_sample.csv`
- `mitigation_results_sample.csv`
- `measures.dax`
- `power_query_group_metrics.m`
- `power_query_mitigation_results.m`
- `dashboard_schema.md`
- `dashboard_layout.json`
- `CivicPulse_Dashboard_Build_Guide.md`

## Save Instructions

1. Open Power BI Desktop.
2. Import `powerbi/group_metrics_sample.csv`.
3. Import `powerbi/mitigation_results_sample.csv`.
4. Add the measures from `powerbi/measures.dax`.
5. Build the pages described in `powerbi/CivicPulse_Dashboard_Build_Guide.md`.
6. Save the report as:

```text
C:\Users\sneha_2\OneDrive\Documents\CivicPulse\powerbi\CivicPulse_Fairness_Dashboard.pbix
```

After the file exists, commit it to GitHub or add it through Git LFS if the file is too large.
