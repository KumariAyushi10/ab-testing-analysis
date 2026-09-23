/* ============================================================
   NovaCart One-Click Checkout A/B Test -- SQL Analysis
   Database: data/novacart_ab_test.db (SQLite)
   Table:    ab_test_sessions

   Run these with:
     sqlite3 data/novacart_ab_test.db
     .read sql/01_analysis_queries.sql

   Or open the .db file in DB Browser for SQLite and paste queries
   into the "Execute SQL" tab.
   ============================================================ */


/* ------------------------------------------------------------
   1. Overall conversion rate by test group
   ------------------------------------------------------------ */
SELECT
    test_group,
    COUNT(*)                                   AS total_sessions,
    SUM(converted)                             AS total_conversions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2) AS conversion_rate_pct
FROM ab_test_sessions
GROUP BY test_group
ORDER BY test_group;


/* ------------------------------------------------------------
   2. Average order value (AOV) -- converted sessions only
   ------------------------------------------------------------ */
SELECT
    test_group,
    COUNT(*)                        AS orders,
    ROUND(AVG(order_value_usd), 2)  AS avg_order_value_usd,
    ROUND(SUM(order_value_usd), 2)  AS total_revenue_usd
FROM ab_test_sessions
WHERE converted = 1
GROUP BY test_group
ORDER BY test_group;


/* ------------------------------------------------------------
   3. Cart abandonment rate by group
      (abandoned = added to cart but did NOT convert)
   ------------------------------------------------------------ */
SELECT
    test_group,
    SUM(added_to_cart)                                        AS carts_started,
    SUM(abandoned_cart)                                       AS carts_abandoned,
    ROUND(100.0 * SUM(abandoned_cart) / NULLIF(SUM(added_to_cart), 0), 2) AS abandonment_rate_pct
FROM ab_test_sessions
GROUP BY test_group
ORDER BY test_group;


/* ------------------------------------------------------------
   4. Conversion rate by group AND device type
      (checks whether the effect is consistent across devices)
   ------------------------------------------------------------ */
SELECT
    device_type,
    test_group,
    COUNT(*)                                    AS sessions,
    SUM(converted)                              AS conversions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2)  AS conversion_rate_pct
FROM ab_test_sessions
GROUP BY device_type, test_group
ORDER BY device_type, test_group;


/* ------------------------------------------------------------
   5. Conversion rate by group AND traffic source
   ------------------------------------------------------------ */
SELECT
    traffic_source,
    test_group,
    COUNT(*)                                    AS sessions,
    SUM(converted)                              AS conversions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2)  AS conversion_rate_pct
FROM ab_test_sessions
GROUP BY traffic_source, test_group
ORDER BY traffic_source, test_group;


/* ------------------------------------------------------------
   6. New vs. returning visitor performance by group
   ------------------------------------------------------------ */
SELECT
    CASE WHEN new_visitor = 1 THEN 'New Visitor' ELSE 'Returning Visitor' END AS visitor_type,
    test_group,
    COUNT(*)                                    AS sessions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2)  AS conversion_rate_pct
FROM ab_test_sessions
GROUP BY visitor_type, test_group
ORDER BY visitor_type, test_group;


/* ------------------------------------------------------------
   7. Average checkout time by group
      (does the "one-click" flow actually save time?)
   ------------------------------------------------------------ */
SELECT
    test_group,
    ROUND(AVG(checkout_time_seconds), 1) AS avg_checkout_time_sec,
    ROUND(MIN(checkout_time_seconds), 1) AS min_checkout_time_sec,
    ROUND(MAX(checkout_time_seconds), 1) AS max_checkout_time_sec
FROM ab_test_sessions
GROUP BY test_group
ORDER BY test_group;


/* ------------------------------------------------------------
   8. Daily conversion rate trend (for a line chart)
   ------------------------------------------------------------ */
SELECT
    DATE(session_timestamp)                      AS session_date,
    test_group,
    COUNT(*)                                     AS sessions,
    SUM(converted)                                AS conversions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2)   AS conversion_rate_pct
FROM ab_test_sessions
GROUP BY session_date, test_group
ORDER BY session_date, test_group;


/* ------------------------------------------------------------
   9. Revenue per session (a blended metric: conversion x AOV)
   ------------------------------------------------------------ */
SELECT
    test_group,
    COUNT(*)                                                AS total_sessions,
    ROUND(SUM(order_value_usd), 2)                          AS total_revenue_usd,
    ROUND(SUM(order_value_usd) * 1.0 / COUNT(*), 3)         AS revenue_per_session_usd
FROM ab_test_sessions
GROUP BY test_group
ORDER BY test_group;


/* ------------------------------------------------------------
   10. Country-level breakdown (top markets)
   ------------------------------------------------------------ */
SELECT
    country,
    test_group,
    COUNT(*)                                    AS sessions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2)  AS conversion_rate_pct,
    ROUND(AVG(CASE WHEN converted = 1 THEN order_value_usd END), 2) AS avg_order_value_usd
FROM ab_test_sessions
GROUP BY country, test_group
ORDER BY country, test_group;
