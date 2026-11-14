-- Datamart layer: pre-aggregated tables the dashboard reads from.

DROP TABLE IF EXISTS dm_daily_sales;
CREATE TABLE dm_daily_sales AS
SELECT
    o.order_date                                   AS sales_date,
    COUNT(DISTINCT o.order_id)                     AS orders,
    SUM(oi.quantity)                               AS units_sold,
    ROUND(SUM(oi.quantity * p.unit_price), 2)      AS revenue,
    ROUND(SUM(oi.quantity * (p.unit_price - p.unit_cost)), 2) AS profit,
    ROUND(100.0 * SUM(oi.quantity * (p.unit_price - p.unit_cost))
          / NULLIF(SUM(oi.quantity * p.unit_price), 0), 2)    AS profit_margin_pct
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p     ON p.product_id = oi.product_id
WHERE o.status = 'completed'
GROUP BY o.order_date;

DROP TABLE IF EXISTS dm_category_sales;
CREATE TABLE dm_category_sales AS
SELECT
    substr(o.order_date, 1, 7)                     AS sales_month,
    p.category,
    SUM(oi.quantity)                               AS units_sold,
    ROUND(SUM(oi.quantity * p.unit_price), 2)      AS revenue,
    ROUND(SUM(oi.quantity * (p.unit_price - p.unit_cost)), 2) AS profit
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p     ON p.product_id = oi.product_id
WHERE o.status = 'completed'
GROUP BY substr(o.order_date, 1, 7), p.category;

DROP TABLE IF EXISTS dm_customer_ltv;
CREATE TABLE dm_customer_ltv AS
SELECT
    c.customer_id,
    c.customer_name,
    c.city,
    COUNT(DISTINCT o.order_id)                     AS orders,
    ROUND(SUM(oi.quantity * p.unit_price), 2)      AS lifetime_value,
    MIN(o.order_date)                              AS first_order,
    MAX(o.order_date)                              AS last_order
FROM customers c
JOIN orders o       ON o.customer_id = c.customer_id AND o.status = 'completed'
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p     ON p.product_id = oi.product_id
GROUP BY c.customer_id, c.customer_name, c.city;

DROP TABLE IF EXISTS dm_payment_mix;
CREATE TABLE dm_payment_mix AS
SELECT
    method,
    COUNT(*)                                       AS payments,
    ROUND(SUM(amount), 2)                          AS amount
FROM payments
GROUP BY method;
