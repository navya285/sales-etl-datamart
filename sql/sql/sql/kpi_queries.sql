-- Example analysis queries on the datamart (use these for your dashboard)

-- 1. Month-over-month revenue and growth
SELECT sales_month, revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY sales_month))
             / LAG(revenue) OVER (ORDER BY sales_month), 2) AS mom_growth_pct
FROM (SELECT substr(sales_date,1,7) AS sales_month, SUM(revenue) AS revenue
      FROM dm_daily_sales GROUP BY 1);

-- 2. Top 10 customers by lifetime value
SELECT customer_name, city, orders, lifetime_value
FROM dm_customer_ltv ORDER BY lifetime_value DESC LIMIT 10;

-- 3. Profit by category
SELECT category, SUM(revenue) AS revenue, SUM(profit) AS profit
FROM dm_category_sales GROUP BY category ORDER BY profit DESC;

-- 4. Days with margin below the overall average (root-cause candidates)
SELECT sales_date, revenue, profit_margin_pct
FROM dm_daily_sales
WHERE profit_margin_pct < (SELECT AVG(profit_margin_pct) FROM dm_daily_sales)
ORDER BY profit_margin_pct;

-- 5. Cancelled / failed order rate by month
SELECT substr(order_date,1,7) AS month,
       ROUND(100.0 * SUM(status <> 'completed') / COUNT(*), 2) AS non_completed_pct
FROM orders GROUP BY 1 ORDER BY 1;
