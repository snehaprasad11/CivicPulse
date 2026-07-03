# CivicPulse Demo Scenario

## Title

CivicPulse: Auditing Fairness in Housing Assistance Allocation

## Scenario

A city housing department uses a scoring model to prioritize applicants for emergency rental assistance. The model is accurate on paper, but community advocates worry that applicants from some districts may be approved at lower rates even when their need is similar.

The policy analyst opens CivicPulse and runs a fairness audit across `district`.

## Demo Flow

1. **Open the dashboard**
   - CivicPulse loads the sample housing-assistance dataset.
   - The analyst sees the main fairness KPIs.

2. **Identify adverse impact**
   - North has the highest positive decision rate.
   - South has the lowest positive decision rate.
   - The disparate impact ratio is `0.33`, which is below the common `0.80` warning threshold.

3. **Inspect explainability**
   - SHAP ranks the most influential signals.
   - LIME explains how the signal changes approval likelihood for a representative applicant.

4. **Simulate mitigation**
   - The analyst compares baseline thresholding against group threshold adjustment and reweighting simulation.
   - The trade-off table shows how fairness improves while accuracy may change.

5. **Compare model strategies**
   - Logistic regression, XGBoost, and PyTorch adversarial debiasing are benchmarked.
   - The adversarial model demonstrates the deep-learning fairness component.

6. **Export for stakeholders**
   - Group metrics and mitigation results can be downloaded as CSVs for Power BI.
   - Ollama can generate a plain-English summary for non-technical review.

## Voiceover Script

City agencies increasingly use models to prioritize scarce public resources. CivicPulse helps policy analysts audit those systems before they affect real people.

In this demo, we audit a housing-assistance scoring model by district. The dashboard immediately shows a warning: one district receives positive decisions far less often than the reference group.

CivicPulse computes fairness metrics from scratch, including disparate impact, demographic parity, equal opportunity, and equalized odds. Here, the disparate impact ratio is 0.33, well below the common 0.80 warning threshold.

The analyst can inspect SHAP and LIME explanations to understand which features are driving model behavior. These explanations turn the black-box score into evidence that can be discussed by policy teams.

Next, the mitigation simulator compares baseline thresholding with group threshold adjustment and reweighting. CivicPulse does not prescribe policy automatically; it shows trade-offs between accuracy and fairness.

Finally, the benchmark view compares logistic regression, XGBoost, and a PyTorch adversarial debiasing neural network. This makes the fairness-accuracy trade-off concrete and reproducible.

The audit can be exported to Power BI or stored in Supabase, giving city teams a practical workflow for algorithmic accountability.
