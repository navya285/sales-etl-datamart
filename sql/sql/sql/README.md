# Sales ETL Pipeline & KPI Datamart (Python + SQL)

An end-to-end pipeline that loads raw sales CSVs, validates them, builds a SQL datamart,
checks the numbers reconcile, and exports tables for a dashboard.

## Flow
CSV files -> Extract (pandas) -> Validate/clean -> Load (normalized tables) -> Datamart (SQL) -> Reconcile -> Dashboard CSVs

## Run
    pip install pandas
    python generate_sample_data.py   # skip if you use your own CSVs in /data
    python etl_pipeline.py

## What it does
- Validates 5 source tables: duplicate IDs, unknown customers, orphan order lines, non-positive quantities, negative payments.
- Writes every rejected row and the reason to dashboard_exports/rejected_rows.csv.
- Builds four datamart tables: dm_daily_sales, dm_category_sales, dm_customer_ltv, dm_payment_mix.
- Reconciles datamart revenue against the source tables and stops if they differ.
- sql/kpi_queries.sql has revenue growth, top customers, category profit, low-margin days and cancellation rate.

## Dashboard (Power BI / Tableau Public)
Connect to the CSVs in dashboard_exports. Suggested pages:
1. Revenue, profit and margin by day/month (dm_daily_sales)
2. Revenue and profit by category (dm_category_sales)
3. Top customers by lifetime value (dm_customer_ltv)
4. Payment method mix (dm_payment_mix)

## Note
Sample data is synthetic. Replace the CSVs in /data with real exports (same column names) to use your own.
