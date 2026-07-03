# Kaggle Publication

Use `civicpulse_kaggle_starter.ipynb` as the public notebook scaffold.

Recommended final notebook flow:

1. Load a public allocation or lending-adjacent dataset.
2. Normalize it with `scripts/prepare_public_dataset.py`.
3. Train baseline logistic regression and XGBoost models.
4. Run CivicPulse fairness metrics from scratch.
5. Add SHAP/LIME explanation plots.
6. Train the PyTorch adversarial debiasing model.
7. Compare fairness and accuracy before/after mitigation.
8. Publish the notebook as a fairness-audit case study rather than a prediction-only notebook.
