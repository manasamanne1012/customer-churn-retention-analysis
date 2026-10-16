import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import os
import shap

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "final_xgb_model.pkl"
)

THRESHOLD_PATH = os.path.join(
    BASE_DIR,
    "models",
    "model_threshold.json"
)


# ------------------------------------------------------------
# Load model and threshold
# ------------------------------------------------------------

@st.cache_resource
def load_model():

    model = joblib.load(MODEL_PATH)

    with open(THRESHOLD_PATH, "r") as f:
        threshold_config = json.load(f)

    threshold = threshold_config["threshold"]

    return model, threshold


model, threshold = load_model()

@st.cache_resource
def load_explainer():
    fitted_xgb = model.named_steps["classifier"]
    return shap.TreeExplainer(fitted_xgb)


explainer = load_explainer()

st.set_page_config(
    page_title="Customer Churn Intelligence",
    page_icon="📊",
    layout="wide"
)

# ------------------------------------------------------------
# Dashboard data
# ------------------------------------------------------------

PROCESSED_DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "telco_customer_churn_clean.csv"
)

RETENTION_DATA_PATH = os.path.join(
    BASE_DIR,
    "reports",
    "customer_retention_scores.csv"
)

@st.cache_data
def load_retention_data():
    return pd.read_csv(RETENTION_DATA_PATH)


retention_data = load_retention_data()

@st.cache_data
def load_dashboard_data():
    return pd.read_csv(PROCESSED_DATA_PATH)


dashboard_df = load_dashboard_data()


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

st.title("📊 Customer Churn & Retention Intelligence")

st.markdown(
    """
    An end-to-end customer churn analytics application powered by
    a tuned XGBoost classification model.
    """
)


# ------------------------------------------------------------
# Executive Dashboard
# ------------------------------------------------------------

st.divider()

st.header("📈 Churn Overview")

total_customers = len(dashboard_df)

churned_customers = (
    dashboard_df["Churn"] == "Yes"
).sum()

churn_rate = (
    churned_customers / total_customers
)

avg_monthly_charges = dashboard_df[
    "MonthlyCharges"
].mean()

month_to_month_churn = dashboard_df.loc[
    dashboard_df["Contract"] == "Month-to-month",
    "Churn"
].eq("Yes").mean()


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Customers",
        f"{total_customers:,}"
    )

with col2:
    st.metric(
        "Overall Churn Rate",
        f"{churn_rate:.1%}"
    )

with col3:
    st.metric(
        "Avg Monthly Charges",
        f"${avg_monthly_charges:.2f}"
    )

with col4:
    st.metric(
        "Month-to-Month Churn",
        f"{month_to_month_churn:.1%}"
    )


st.divider()

chart_col1, chart_col2 = st.columns(2)

with chart_col1:

    st.subheader("Churn by Contract")

    contract_churn = (
        dashboard_df
        .groupby("Contract")["Churn"]
        .apply(lambda x: (x == "Yes").mean())
        .reset_index(name="Churn Rate")
    )

    st.bar_chart(
        contract_churn.set_index("Contract")
    )


with chart_col2:

    st.subheader("Churn by Internet Service")

    internet_churn = (
        dashboard_df
        .groupby("InternetService")["Churn"]
        .apply(lambda x: (x == "Yes").mean())
        .reset_index(name="Churn Rate")
    )

    st.bar_chart(
        internet_churn.set_index("InternetService")
    )

# ------------------------------------------------------------
# Model Risk Dashboard
# ------------------------------------------------------------

st.divider()

st.header("🎯 Model Risk Distribution")

risk_counts = (
    retention_data["risk_segment"]
    .value_counts()
    .reindex(
        ["Low Risk", "Medium Risk", "High Risk"]
    )
    .fillna(0)
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Low Risk",
        f"{int(risk_counts['Low Risk']):,}"
    )

with col2:
    st.metric(
        "Medium Risk",
        f"{int(risk_counts['Medium Risk']):,}"
    )

with col3:
    st.metric(
        "High Risk",
        f"{int(risk_counts['High Risk']):,}"
    )

st.divider()

st.subheader("Customers by Risk Segment")

st.bar_chart(
    risk_counts
)

st.divider()

st.subheader("Observed Churn by Risk Segment")

risk_validation = (
    retention_data
    .groupby("risk_segment", observed=True)
    .agg(
        customers=("actual_churn", "size"),
        actual_churners=("actual_churn", "sum"),
        avg_predicted_probability=("churn_probability", "mean")
    )
    .reindex(
        ["Low Risk", "Medium Risk", "High Risk"]
    )
)

risk_validation["actual_churn_rate"] = (
    risk_validation["actual_churners"]
    / risk_validation["customers"]
)

display_risk = risk_validation.copy()

display_risk["avg_predicted_probability"] = (
    display_risk["avg_predicted_probability"]
    .map(lambda x: f"{x:.1%}")
)

display_risk["actual_churn_rate"] = (
    display_risk["actual_churn_rate"]
    .map(lambda x: f"{x:.1%}")
)

display_risk.columns = [
    "Customers",
    "Actual Churners",
    "Avg Predicted Risk",
    "Observed Churn Rate"
]

st.dataframe(
    display_risk,
    use_container_width=True
)

# ------------------------------------------------------------
# Retention Opportunity
# ------------------------------------------------------------

st.divider()

st.header("💡 Retention Opportunity")

retention_data["priority"] = np.where(
    retention_data["risk_segment"] == "High Risk",
    "High Priority",
    np.where(
        retention_data["risk_segment"] == "Medium Risk",
        "Medium Priority",
        "Standard"
    )
)

priority_summary = (
    retention_data
    .groupby("priority")
    .agg(
        customers=("actual_churn", "size"),
        actual_churners=("actual_churn", "sum"),
        monthly_charge_exposure=("MonthlyCharges", "sum"),
        avg_churn_probability=("churn_probability", "mean")
    )
)

priority_summary["actual_churn_rate"] = (
    priority_summary["actual_churners"]
    / priority_summary["customers"]
)

priority_summary = priority_summary.reindex(
    ["High Priority", "Medium Priority", "Standard"]
)

# KPI cards

col1, col2, col3 = st.columns(3)

with col1:
    high_risk_customers = int(
        priority_summary.loc[
            "High Priority",
            "customers"
        ]
    )

    st.metric(
        "High-Priority Customers",
        f"{high_risk_customers:,}"
    )

with col2:
    high_risk_exposure = (
        priority_summary.loc[
            "High Priority",
            "monthly_charge_exposure"
        ]
    )

    st.metric(
        "High-Risk Monthly Charges",
        f"${high_risk_exposure:,.2f}"
    )

with col3:
    high_risk_churn_rate = (
        priority_summary.loc[
            "High Priority",
            "actual_churn_rate"
        ]
    )

    st.metric(
        "High-Risk Observed Churn",
        f"{high_risk_churn_rate:.1%}"
    )

st.divider()

st.subheader("Retention Actions")

action_counts = (
    retention_data
    .groupby("priority")
    .size()
    .reindex(
        ["High Priority", "Medium Priority", "Standard"]
    )
    .fillna(0)
)

st.bar_chart(action_counts)

st.divider()

st.subheader("Priority Customer Queue")

priority_customers = (
    retention_data[
        retention_data["priority"].isin(
            ["High Priority", "Medium Priority"]
        )
    ]
    .sort_values(
        "churn_probability",
        ascending=False
    )
    .copy()
)

priority_display = priority_customers[
    [
        "Contract",
        "tenure",
        "MonthlyCharges",
        "InternetService",
        "OnlineSecurity",
        "TechSupport",
        "churn_probability",
        "priority"
    ]
].head(20)

priority_display["churn_probability"] = (
    priority_display["churn_probability"]
    .map(lambda x: f"{x:.1%}")
)

st.dataframe(
    priority_display,
    use_container_width=True,
    hide_index=True
)


# ------------------------------------------------------------
# Model information
# ------------------------------------------------------------
st.divider()

st.subheader("Model Information")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Model", "Tuned XGBoost")

with col2:
    st.metric("ROC-AUC", "0.8429")

with col3:
    st.metric("Operating Threshold", f"{threshold:.2f}")


st.info(
    f"Customers with predicted churn probability ≥ "
    f"{threshold:.0%} are flagged for retention review."
)

st.divider()

st.header("🔎 Customer Churn Prediction")

st.write(
    "Enter customer details to estimate churn probability "
    "and determine the retention risk level."
)


# ------------------------------------------------------------
# Customer inputs
# ------------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:

    gender = st.selectbox(
        "Gender",
        ["Female", "Male"]
    )

    senior_citizen = st.selectbox(
        "Senior Citizen",
        [0, 1]
    )

    partner = st.selectbox(
        "Partner",
        ["Yes", "No"]
    )

    dependents = st.selectbox(
        "Dependents",
        ["Yes", "No"]
    )

    tenure = st.number_input(
        "Tenure (months)",
        min_value=0,
        max_value=72,
        value=12
    )


with col2:

    phone_service = st.selectbox(
        "Phone Service",
        ["Yes", "No"]
    )

    multiple_lines = st.selectbox(
        "Multiple Lines",
        ["Yes", "No", "No phone service"]
    )

    internet_service = st.selectbox(
        "Internet Service",
        ["DSL", "Fiber optic", "No"]
    )

    online_security = st.selectbox(
        "Online Security",
        ["Yes", "No", "No internet service"]
    )

    online_backup = st.selectbox(
        "Online Backup",
        ["Yes", "No", "No internet service"]
    )

    device_protection = st.selectbox(
        "Device Protection",
        ["Yes", "No", "No internet service"]
    )

    tech_support = st.selectbox(
        "Tech Support",
        ["Yes", "No", "No internet service"]
    )


with col3:

    streaming_tv = st.selectbox(
        "Streaming TV",
        ["Yes", "No", "No internet service"]
    )

    streaming_movies = st.selectbox(
        "Streaming Movies",
        ["Yes", "No", "No internet service"]
    )

    contract = st.selectbox(
        "Contract",
        ["Month-to-month", "One year", "Two year"]
    )

    paperless_billing = st.selectbox(
        "Paperless Billing",
        ["Yes", "No"]
    )

    payment_method = st.selectbox(
        "Payment Method",
        [
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)"
        ]
    )

    monthly_charges = st.number_input(
        "Monthly Charges",
        min_value=0.0,
        max_value=200.0,
        value=70.0
    )

    total_charges = st.number_input(
        "Total Charges",
        min_value=0.0,
        max_value=10000.0,
        value=1000.0
    )

# ------------------------------------------------------------
# Feature engineering for prediction
# ------------------------------------------------------------

if tenure > 0:
    avg_monthly_value = total_charges / tenure
else:
    avg_monthly_value = monthly_charges


service_count = sum([
    phone_service == "Yes",
    multiple_lines == "Yes",
    online_security == "Yes",
    online_backup == "Yes",
    device_protection == "Yes",
    tech_support == "Yes",
    streaming_tv == "Yes",
    streaming_movies == "Yes"
])


# ------------------------------------------------------------
# Create prediction dataframe
# ------------------------------------------------------------

customer_data = pd.DataFrame([{
    "gender": gender,
    "SeniorCitizen": senior_citizen,
    "Partner": partner,
    "Dependents": dependents,
    "tenure": tenure,
    "PhoneService": phone_service,
    "MultipleLines": multiple_lines,
    "InternetService": internet_service,
    "OnlineSecurity": online_security,
    "OnlineBackup": online_backup,
    "DeviceProtection": device_protection,
    "TechSupport": tech_support,
    "StreamingTV": streaming_tv,
    "StreamingMovies": streaming_movies,
    "Contract": contract,
    "PaperlessBilling": paperless_billing,
    "PaymentMethod": payment_method,
    "MonthlyCharges": monthly_charges,
    "TotalCharges": total_charges,
    "avg_monthly_value": avg_monthly_value,
    "service_count": service_count
}])


# ------------------------------------------------------------
# Prediction
# ------------------------------------------------------------

if st.button("Predict Churn", type="primary"):

    churn_probability = model.predict_proba(
        customer_data
    )[0, 1]

    predicted_churn = int(
        churn_probability >= threshold
    )

    st.divider()

    st.subheader("Prediction Result")

    result_col1, result_col2, result_col3 = st.columns(3)

    with result_col1:
        st.metric(
            "Churn Probability",
            f"{churn_probability:.1%}"
        )

    with result_col2:
        st.metric(
            "Risk Threshold",
            f"{threshold:.0%}"
        )

    with result_col3:

        if predicted_churn:
            st.error("HIGH RISK")
        else:
            st.success("LOWER RISK")

    if predicted_churn:
        st.warning(
            "This customer is above the model's operating "
            "threshold and should be considered for retention outreach."
        )
    else:
        st.success(
            "This customer's predicted churn probability is "
            "below the operating threshold."
        )

    # --------------------------------------------------------
    # SHAP explanation
    # --------------------------------------------------------

    st.divider()
    st.subheader("🔍 Why did the model make this prediction?")

    fitted_preprocessor = model.named_steps["preprocessor"]

    customer_transformed = fitted_preprocessor.transform(
        customer_data
    )

    shap_values_customer = explainer.shap_values(
        customer_transformed
    )

    feature_names = fitted_preprocessor.get_feature_names_out()

    shap_df = pd.DataFrame({
        "feature": feature_names,
        "shap_value": shap_values_customer[0]
    })

    shap_df["impact"] = shap_df["shap_value"].abs()

    shap_df = shap_df.sort_values(
        "impact",
        ascending=False
    ).head(10)

    shap_df["direction"] = np.where(
    shap_df["shap_value"] > 0,
    "Increases churn risk",
    "Decreases churn risk"
    )


    # Clean preprocessing prefixes and feature names
    shap_df["feature"] = (
    shap_df["feature"]
    .str.replace("cat__", "", regex=False)
    .str.replace("num__", "", regex=False)
    .str.replace("_", " ", regex=False)
    )

    shap_df["feature"] = shap_df["feature"].str.replace(
    "Month-to-month",
    "Month-to-month contract",
    regex=False
    )

    display_df = shap_df[
    [
        "feature",
        "shap_value",
        "direction"
    ]
    ].copy()

    display_df["shap_value"] = display_df["shap_value"].round(3)

    display_df.columns = [
    "Feature",
    "SHAP Impact",
    "Direction"
    ]

    st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
    )

    # --------------------------------------------------------
    # Suggested retention action
    # --------------------------------------------------------

    st.divider()
    st.subheader("💡 Suggested Retention Action")

    if predicted_churn:

        if contract == "Month-to-month":
            recommendation = (
                "Consider a contract retention or upgrade offer."
            )

        elif tech_support == "No" and online_security == "No":
            recommendation = (
                "Consider a support and security bundle."
            )

        elif monthly_charges >= 70:
            recommendation = (
                "Consider a high-value customer retention review."
            )

        elif tech_support == "No":
            recommendation = (
                "Consider proactive technical support outreach."
            )

        elif online_security == "No":
            recommendation = (
                "Consider a security-focused engagement offer."
            )

        else:
            recommendation = (
                "Consider priority retention outreach."
            )

        st.warning(recommendation)

    else:

        st.success(
            "No immediate retention intervention is indicated "
            "by the current model threshold."
        )
