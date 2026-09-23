SELECT
    test_group,
    COUNT(*)                                   AS total_sessions,
    SUM(converted)                             AS total_conversions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2) AS conversion_rate_pct
FROM ab_test_sessions
GROUP BY test_group
ORDER BY test_group;



SELECT
    test_group,
    COUNT(*)                        AS orders,
    ROUND(AVG(order_value_usd), 2)  AS avg_order_value_usd,
    ROUND(SUM(order_value_usd), 2)  AS total_revenue_usd
FROM ab_test_sessions
WHERE converted = 1
GROUP BY test_group
ORDER BY test_group;



SELECT
    test_group,
    SUM(added_to_cart)                                        AS carts_started,
    SUM(abandoned_cart)                                       AS carts_abandoned,
    ROUND(100.0 * SUM(abandoned_cart) / NULLIF(SUM(added_to_cart), 0), 2) AS abandonment_rate_pct
FROM ab_test_sessions
GROUP BY test_group
ORDER BY test_group;



SELECT
    device_type,
    test_group,
    COUNT(*)                                    AS sessions,
    SUM(converted)                              AS conversions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2)  AS conversion_rate_pct
FROM ab_test_sessions
GROUP BY device_type, test_group
ORDER BY device_type, test_group;



SELECT
    traffic_source,
    test_group,
    COUNT(*)                                    AS sessions,
    SUM(converted)                              AS conversions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2)  AS conversion_rate_pct
FROM ab_test_sessions
GROUP BY traffic_source, test_group
ORDER BY traffic_source, test_group;



SELECT
    CASE WHEN new_visitor = 1 THEN 'New Visitor' ELSE 'Returning Visitor' END AS visitor_type,
    test_group,
    COUNT(*)                                    AS sessions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2)  AS conversion_rate_pct
FROM ab_test_sessions
GROUP BY visitor_type, test_group
ORDER BY visitor_type, test_group;



SELECT
    test_group,
    ROUND(AVG(checkout_time_seconds), 1) AS avg_checkout_time_sec,
    ROUND(MIN(checkout_time_seconds), 1) AS min_checkout_time_sec,
    ROUND(MAX(checkout_time_seconds), 1) AS max_checkout_time_sec
FROM ab_test_sessions
GROUP BY test_group
ORDER BY test_group;



SELECT
    DATE(session_timestamp)                      AS session_date,
    test_group,
    COUNT(*)                                     AS sessions,
    SUM(converted)                                AS conversions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2)   AS conversion_rate_pct
FROM ab_test_sessions
GROUP BY session_date, test_group
ORDER BY session_date, test_group;



SELECT
    test_group,
    COUNT(*)                                                AS total_sessions,
    ROUND(SUM(order_value_usd), 2)                          AS total_revenue_usd,
    ROUND(SUM(order_value_usd) * 1.0 / COUNT(*), 3)         AS revenue_per_session_usd
FROM ab_test_sessions
GROUP BY test_group
ORDER BY test_group;



SELECT
    country,
    test_group,
    COUNT(*)                                    AS sessions,
    ROUND(100.0 * SUM(converted) / COUNT(*), 2)  AS conversion_rate_pct,
    ROUND(AVG(CASE WHEN converted = 1 THEN order_value_usd END), 2) AS avg_order_value_usd
FROM ab_test_sessions
GROUP BY country, test_group
ORDER BY country, test_group;
