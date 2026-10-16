
-- CUSTOMER CHURN PREDICTION & RETENTION INTELLIGENCE
-- MySQL Analytics Layer
-- Database: churn_analytics

USE churn_analytics;


-- 1. OVERALL CHURN KPI

SELECT
    COUNT(*) AS total_customers,

    SUM(
        CASE
            WHEN Churn = 'Yes' THEN 1
            ELSE 0
        END
    ) AS churned_customers,

    SUM(
        CASE
            WHEN Churn = 'No' THEN 1
            ELSE 0
        END
    ) AS retained_customers,

    ROUND(
        100.0 *
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS churn_rate

FROM telco_customer_churn;


-- 2. CHURN BY CONTRACT

SELECT
    Contract,

    COUNT(*) AS customers,

    SUM(
        CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END
    ) AS churned_customers,

    ROUND(
        100.0 *
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS churn_rate

FROM telco_customer_churn

GROUP BY Contract

ORDER BY churn_rate DESC;


-- 3. CHURN BY TENURE GROUP

SELECT

    CASE
        WHEN tenure <= 6 THEN '0-6 Months'
        WHEN tenure <= 12 THEN '7-12 Months'
        WHEN tenure <= 24 THEN '13-24 Months'
        WHEN tenure <= 48 THEN '25-48 Months'
        ELSE '49-72 Months'
    END AS tenure_group,

    COUNT(*) AS customers,

    SUM(
        CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END
    ) AS churned_customers,

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
    END

ORDER BY churn_rate DESC;


-- 4. CHURN BY PAYMENT METHOD

SELECT
    PaymentMethod,

    COUNT(*) AS customers,

    SUM(
        CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END
    ) AS churned_customers,

    ROUND(
        100.0 *
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS churn_rate

FROM telco_customer_churn

GROUP BY PaymentMethod

ORDER BY churn_rate DESC;


-- 5. CHURN BY INTERNET SERVICE

SELECT
    InternetService,

    COUNT(*) AS customers,

    SUM(
        CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END
    ) AS churned_customers,

    ROUND(
        100.0 *
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS churn_rate

FROM telco_customer_churn

GROUP BY InternetService

ORDER BY churn_rate DESC;


-- 6. CHURN BY SUPPORT & SECURITY

SELECT
    TechSupport,
    OnlineSecurity,

    COUNT(*) AS customers,

    SUM(
        CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END
    ) AS churned_customers,

    ROUND(
        100.0 *
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS churn_rate

FROM telco_customer_churn

GROUP BY
    TechSupport,
    OnlineSecurity

ORDER BY churn_rate DESC;


-- 7. CHURN BY SENIOR CITIZEN STATUS

SELECT
    SeniorCitizen,

    COUNT(*) AS customers,

    SUM(
        CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END
    ) AS churned_customers,

    ROUND(
        100.0 *
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS churn_rate

FROM telco_customer_churn

GROUP BY SeniorCitizen

ORDER BY churn_rate DESC;


-- 8. CHURN BY PAPERLESS BILLING

SELECT
    PaperlessBilling,

    COUNT(*) AS customers,

    SUM(
        CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END
    ) AS churned_customers,

    ROUND(
        100.0 *
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS churn_rate

FROM telco_customer_churn

GROUP BY PaperlessBilling

ORDER BY churn_rate DESC;


-- 9. CHURN AND REVENUE PROFILE

SELECT
    Churn,

    COUNT(*) AS customers,

    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,

    ROUND(AVG(TotalCharges), 2) AS avg_total_charges,

    ROUND(SUM(MonthlyCharges), 2) AS total_monthly_charges

FROM telco_customer_churn

GROUP BY Churn;


-- 10. HIGH-VALUE CHURN CUSTOMERS

SELECT
    customerID,
    Contract,
    tenure,
    MonthlyCharges,
    TotalCharges,
    InternetService,
    OnlineSecurity,
    TechSupport,
    Churn

FROM telco_customer_churn

WHERE Churn = 'Yes'

  AND MonthlyCharges >= (
      SELECT AVG(MonthlyCharges)
      FROM telco_customer_churn
  )

ORDER BY MonthlyCharges DESC;


-- 11. NEW CUSTOMER CHURN RISK

SELECT
    Contract,
    COUNT(*) AS customers,

    SUM(
        CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END
    ) AS churned_customers,

    ROUND(
        100.0 *
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS churn_rate

FROM telco_customer_churn

WHERE tenure <= 6

GROUP BY Contract

ORDER BY churn_rate DESC;


-- 12. CONTRACT + INTERNET SERVICE SEGMENTATION

SELECT
    Contract,
    InternetService,

    COUNT(*) AS customers,

    SUM(
        CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END
    ) AS churned_customers,

    ROUND(
        100.0 *
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS churn_rate

FROM telco_customer_churn

GROUP BY
    Contract,
    InternetService

HAVING COUNT(*) >= 20

ORDER BY churn_rate DESC;


-- 13. PAYMENT METHOD + CONTRACT SEGMENTATION

SELECT
    PaymentMethod,
    Contract,

    COUNT(*) AS customers,

    SUM(
        CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END
    ) AS churned_customers,

    ROUND(
        100.0 *
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS churn_rate

FROM telco_customer_churn

GROUP BY
    PaymentMethod,
    Contract

HAVING COUNT(*) >= 20

ORDER BY churn_rate DESC;


-- 14. HIGH MONTHLY CHARGE CUSTOMERS

SELECT
    Contract,

    COUNT(*) AS customers,

    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,

    ROUND(
        100.0 *
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS churn_rate

FROM telco_customer_churn

WHERE MonthlyCharges >= (
    SELECT
        AVG(MonthlyCharges)
    FROM telco_customer_churn
)

GROUP BY Contract

ORDER BY churn_rate DESC;


-- 15. RETENTION TARGET SEGMENT

SELECT
    Contract,
    InternetService,
    TechSupport,
    OnlineSecurity,

    COUNT(*) AS customers,

    SUM(
        CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END
    ) AS churned_customers,

    ROUND(
        100.0 *
        SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS churn_rate,

    ROUND(
        SUM(MonthlyCharges),
        2
    ) AS monthly_charge_exposure

FROM telco_customer_churn

WHERE Contract = 'Month-to-month'

GROUP BY
    Contract,
    InternetService,
    TechSupport,
    OnlineSecurity

HAVING COUNT(*) >= 20

ORDER BY churn_rate DESC;