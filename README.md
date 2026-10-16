# Customer Churn Prediction and Retention Analysis

## Overview
This project analyzes customer data to identify customers who are likely to discontinue a service. It combines exploratory data analysis, machine learning, model explainability, and business-oriented retention insights to support data-driven decision-making.

The project uses Python, SQL, machine learning models, and a Streamlit application to explore customer behavior and help prioritize retention efforts.

## Business Problem
Customer churn can reduce recurring revenue and increase customer acquisition costs. By identifying customers at risk of leaving, businesses can investigate churn patterns and prioritize retention strategies.

## Objectives
- Analyze customer data and identify churn patterns.
- Perform data quality checks and exploratory data analysis.
- Prepare customer features for machine learning.
- Compare classification models for churn prediction.
- Use model explainability techniques to understand important factors.
- Translate analytical findings into actionable retention insights.

## Dataset
The project uses the Telco Customer Churn dataset.

- **Number of records:** 7,043
- **Number of columns:** 21, before preprocessing
- **Target variable:** `Churn`
- **Target classes:** Yes and No

The dataset contains customer information related to demographics, account details, services, and billing.

## Technologies Used
- Python
- Pandas and NumPy
- Matplotlib and Seaborn
- Scikit-learn
- XGBoost
- SHAP
- SQL / MySQL
- Streamlit
- Jupyter Notebook

## Machine Learning
The modeling workflow explores customer churn classification using models such as:

- Logistic Regression
- Random Forest
- XGBoost

Model explainability with SHAP can help investigate which features influence model predictions.

Actual model performance should be reported only after evaluating the models on the dataset.

## Project Structure

```text
customer-churn-retention-analysis/
├── app/
├── data/
├── models/
├── notebooks/
│   ├── 01_data_quality_audit.ipynb
│   ├── 02_eda.ipynb
│   └── 03_modeling.ipynb
├── reports/
├── sql/
├── README.md
└── requirements.txt
