# Responsive QA

CivicPulse was checked against desktop, tablet, and phone viewports using the live React app connected to the local FastAPI service.

## Verified Viewports

| Viewport | Evidence | Result |
| --- | --- | --- |
| Desktop, 1600px wide | `docs/assets/dashboard-overview.png` | Metrics, chart, group table, finding, mitigation, explanations, and benchmark are readable. |
| Tablet, 820px wide | `docs/assets/tablet-dashboard.png` | Dashboard sections stack cleanly while retaining readable chart and tables. |
| Phone, 390px wide | `docs/assets/mobile-dashboard.png` | Metric cards stack, toolbar wraps, tables are simplified or horizontally scroll-contained, and page-level horizontal overflow is avoided. |

## Mobile Fixes Applied

- Metric tiles use `sm`/`lg` breakpoints instead of jumping directly from one column to desktop.
- Main grid containers use `min-w-0` so cards can shrink inside narrow viewports.
- Group metrics hide secondary diagnostic columns on phones while preserving the key group, applicant count, and selection-rate values.
- Wider analytical tables are contained inside horizontal scroll regions instead of forcing page-level overflow.
- Recharts bar animation is disabled so screenshots and tests capture stable chart bars.

## Remaining Product Hardening

- Add automated visual regression tests for at least `390x844`, `768x1024`, and `1440x1000`.
- Consider a chart-specific mobile rendering mode if the dashboard grows beyond the current sample dataset.
- Add keyboard-focus styling and screen-reader labels for upload controls before public deployment.
