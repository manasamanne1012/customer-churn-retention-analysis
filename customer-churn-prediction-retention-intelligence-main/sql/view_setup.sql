USE churn_analytics;

-- 1. Overall KPI view
CREATE OR REPLACE VIEW vw_churn_kpis AS
SELECT
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    SUM(CASE WHEN Churn = 'No' THEN 1 ELSE 0 END) AS retained_customers,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS churn_rate
FROM telco_customer_churn;


-- 2. Contract analysis view
CREATE OR REPLACE VIEW vw_contract_churn AS
SELECT
    Contract,
    COUNT(*) AS customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS churn_rate
FROM telco_customer_churn
GROUP BY Contract;


-- 3. Payment analysis view
CREATE OR REPLACE VIEW vw_payment_churn AS
SELECT
    PaymentMethod,
    COUNT(*) AS customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS churn_rate
FROM telco_customer_churn
GROUP BY PaymentMethod;


-- 4. Internet service analysis view
CREATE OR REPLACE VIEW vw_internet_churn AS
SELECT
    InternetService,
    COUNT(*) AS customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(
        100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS churn_rate
FROM telco_customer_churn
GROUP BY InternetService;


-- 5. Tenure analysis view
CREATE OR REPLACE VIEW vw_tenure_churn AS
SELECT
    CASE
        WHEN tenure <= 6 THEN '0-6 Months'
        WHEN tenure <= 12 THEN '7-12 Months'
        WHEN tenure <= 24 THEN '13-24 Months'
        WHEN tenure <= 48 THEN '25-48 Months'
        ELSE '49-72 Months'
    END AS tenure_group,

    COUNT(*) AS customers,

    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)
        AS churned_customers,

    ROUND(
        100.0 *
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS churn_rate

FROM telco_customer_churn

GROUP BY
    CASE
        WHEN tenure <= 6 THEN '0-6 Months'
        WHEN tenure <= 12 THEN '7-12 Months'
        WHEN tenure <= 24 THEN '13-24 Months'
        WHEN tenure <= 48 THEN '25-48 Months'
        ELSE '49-72 Months'
    END;

-- Retention - Target View

CREATE OR REPLACE VIEW vw_retention_targets AS
SELECT
    customerID,
    Contract,
    tenure,
    MonthlyCharges,
    TotalCharges,
    InternetService,
    OnlineSecurity,
    TechSupport,
    PaymentMethod,
    Churn

FROM telco_customer_churn

WHERE Contract = 'Month-to-month'
  AND (
      OnlineSecurity = 'No'
      OR TechSupport = 'No'
  );

  SHOW FULL TABLES
WHERE Table_type = 'VIEW';

SELECT *
FROM vw_churn_kpis;

SELECT *
FROM vw_contract_churn;