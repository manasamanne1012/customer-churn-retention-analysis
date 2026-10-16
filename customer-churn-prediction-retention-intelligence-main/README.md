# Customer Churn Prediction & Retention Intelligence

An end-to-end churn analytics project that turns customer data into a retention-prioritization workflow. It combines data quality checks, exploratory and statistical analysis, supervised machine learning, explainability, MySQL analysis, and an interactive Streamlit application.

## Business problem

Customer churn erodes recurring revenue and is often identified too late for an effective intervention. The goal is to estimate each customer's probability of churn and prioritize retention review for customers whose predicted risk meets a business-oriented operating threshold. The project is designed to support decisions—not to claim that a model prediction proves why a customer will churn or that a recommended offer will cause them to stay.

## Key result

**Tuned XGBoost was selected as the frozen model for the retention-focused operating objective among the evaluated candidates.** On the untouched held-out test set, it achieved:

| Metric | Result |
| --- | ---: |
| ROC-AUC | 0.8429 |
| Recall | 71.93% |
| F1 score | 63.00% |
| Operating threshold | 0.35 |

The threshold is intentional: customers with a churn probability of **35% or more** are flagged for retention review. This prioritizes finding more potential churners over relying on a default 0.50 classification cutoff.

## Dataset and data quality

The project uses the Telco Customer Churn dataset, with one row per customer and demographic, account, service, billing, and churn fields.

- Python analysis and modeling use all **7,043 rows**.
- `TotalCharges` contains **11 blank values**; these are handled during the Python cleaning workflow.
- The MySQL import contains **7,032 rows** because those 11 blank-`TotalCharges` records were not imported by MySQL Workbench.

This difference is documented deliberately. Python-derived metrics and model results should be compared with the 7,043-row analysis; SQL counts should be interpreted within the 7,032-row MySQL table.

## Analysis workflow

1. **Data-quality audit** — inspects schema, duplicates, missing/blank values, types, and target balance.
2. **EDA** — examines churn across contract type, tenure, internet service, payment method, billing, support/security services, and charges.
3. **Statistical testing** — uses chi-square tests for categorical variables and Mann–Whitney U tests for numeric variables to assess whether churned and retained customers differ beyond visual patterns alone. These tests describe association, not causation.
4. **Feature engineering** — includes customer-value and service-adoption features such as `avg_monthly_value` and `service_count`.
5. **Modeling and validation** — compares evaluated classifiers using a held-out test set and selects an operating threshold from validation work for the retention objective.

The analysis consistently focuses attention on actionable retention signals: contract commitment, tenure, service/support configuration, charges, and payment behavior. Exact exploratory outputs and test results are reproducible in the notebooks rather than duplicated selectively here.

## Modeling approach

The modeling notebook uses a reproducible pipeline:

```text
Raw customer data
    -> cleaning + engineered features
    -> categorical encoding + numeric preprocessing
    -> candidate-model evaluation
    -> validation threshold selection
    -> untouched test evaluation
    -> saved XGBoost pipeline + threshold configuration
```

Candidate models are compared in `reports/model_results.csv`; threshold trade-offs are recorded in `reports/model_thresholds.csv`. The selected XGBoost pipeline is saved in `models/final_xgb_model.pkl`, and its 0.35 operating threshold is saved in `models/model_threshold.json`.

### Held-out test comparison

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | Selected threshold |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Standard Logistic Regression | 77.43% | 56.36% | 66.31% | 60.93% | 0.8412 | 0.40 |
| Balanced Logistic Regression | 77.15% | 55.91% | 65.78% | 60.44% | 0.8406 | 0.65 |
| Tuned XGBoost | 77.57% | 56.04% | **71.93%** | **63.00%** | **0.8429** | **0.35** |

Thresholds are selected to reflect the retention workflow, then their final performance is reported on the untouched test set. A lower threshold increases the number of customers reviewed and improves churner coverage at the cost of additional false positives; this is a business capacity trade-off, not a universally optimal cutoff.

Selection is framed correctly: XGBoost was chosen for this retention-oriented operating objective among the models evaluated in this project. It is not presented as universally best for all churn datasets, business costs, or deployment contexts.

## Explainability and retention intelligence

The Streamlit app uses SHAP to show which transformed features most increased or decreased a single customer's predicted risk. SHAP explains the model's local behavior; it does not establish causal drivers.

Held-out customers are also segmented into low-, medium-, and high-risk groups and translated into a practical action queue. The retained reporting layer supports actions such as:

- contract retention or upgrade offers;
- support and security outreach;
- high-value retention review; and
- standard engagement for lower-risk customers.

For example, the held-out retention report identifies a high-priority support, security, and contract-retention group of **140 customers** with **73.57% observed churn** and approximately **69.0% average predicted risk**. The standard-engagement group contains **929 customers** with **11.30% observed churn**. Monthly-charge totals in the report are exposure indicators, not causal estimates of revenue saved or lost.

## MySQL analytics layer

The MySQL layer provides reusable business analysis in `sql/churn_analysis.sql` and `sql/view_setup.sql`, including:

- overall churn KPIs;
- churn by contract, tenure band, payment method, and internet service;
- support/security and revenue-profile analysis;
- high-value churn and new-customer risk segments; and
- reusable views for KPIs, contract, payment, internet, tenure, and retention targets.

The database schema is `churn_analytics`, with the imported table `telco_customer_churn`.

## Streamlit application

The dashboard in `app/app.py` provides:

- executive churn KPIs and segment charts;
- risk distribution and observed-churn validation on held-out scoring output;
- a priority customer queue and retention opportunity view;
- real-time customer scoring with the saved XGBoost pipeline;
- the 0.35 retention threshold; and
- local SHAP explanations plus business-rule retention suggestions.

The model predicts risk; the suggested retention action is a separate business-rule layer.

## Project structure

```text
.
├── app/                 # Streamlit dashboard
├── data/
│   ├── raw/             # source dataset
│   └── processed/       # cleaned analysis dataset
├── models/              # frozen model pipeline and threshold
├── notebooks/           # audit, EDA, and modeling workflow
├── reports/             # model, threshold, risk, and action outputs
└── sql/                 # MySQL queries and views
```

## Run locally

```bash
git clone <your-repository-url>
cd "Customer Churn Prediction & Retention Intelligence"
python -m venv .venv
source .venv/bin/activate            # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app/app.py
```

To use the SQL layer, import `data/raw/telco_customer_churn.csv` into MySQL as `churn_analytics.telco_customer_churn`, then run the scripts in `sql/`. See the dataset note above before reconciling row counts.

## Tech stack

Python, pandas, NumPy, scikit-learn, XGBoost, SHAP, joblib, Jupyter, Streamlit, MySQL, and MySQL Workbench.

## Limitations and next steps

- The data is a static churn dataset, so performance can drift in a live setting and needs monitoring.
- The threshold reflects the current retention objective; it should be recalibrated once outreach capacity, contact cost, and offer value are known.
- SHAP and segment patterns are explanatory associations, not causal evidence.
- Retention recommendations are heuristics and should be tested with controlled experiments before operational rollout.
- A production version should add data validation, model/version tracking, access controls, logging, and outcome feedback for retraining.

## Interview summary

This project demonstrates an end-to-end analytics workflow: audit the data, investigate churn patterns statistically, engineer features, evaluate models responsibly, tune the decision threshold for retention operations, explain individual scores, turn scores into an action queue, and expose the work through SQL and Streamlit.
