SELECT 'customers' AS table_name, COUNT(*) AS total_rows FROM customers
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'sellers', COUNT(*) FROM sellers
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL
SELECT 'order_payments', COUNT(*) FROM order_payments
UNION ALL
SELECT 'order_reviews', COUNT(*) FROM order_reviews
UNION ALL
SELECT 'geolocation', COUNT(*) FROM geolocation
UNION ALL
SELECT 'product_category_name_translation',
       COUNT(*) FROM product_category_name_translation
ORDER BY table_name;

SELECT * FROM orders LIMIT 5;

SELECT COUNT(*) AS total_orders, 
	MIN(order_purchase_timestamp) AS oldest_order, 
	MAX(order_purchase_timestamp) AS latest_order FROM orders;

SELECT order_status, COUNT(*) AS status_count FROM orders
	GROUP BY(order_status)
	ORDER BY(status_count) DESC;

SELECT COUNT(*) AS missing_date FROM orders
	WHERE order_delivered_customer_date IS NULL;

SELECT order_status, COUNT(*) AS missing_date FROM orders
	WHERE order_delivered_customer_date IS NULL
	GROUP BY order_status;

SELECT
    COUNT(*) FILTER (
        WHERE order_purchase_timestamp IS NULL
    ) AS missing_purchase,

    COUNT(*) FILTER (
        WHERE order_approved_at IS NULL
    ) AS missing_approval,

    COUNT(*) FILTER (
        WHERE order_delivered_carrier_date IS NULL
    ) AS missing_carrier_date,

    COUNT(*) FILTER (
        WHERE order_delivered_customer_date IS NULL
    ) AS missing_delivery_date,

    COUNT(*) FILTER (
        WHERE order_estimated_delivery_date IS NULL
    ) AS missing_estimated_date

FROM orders;

SELECT MIN(order_purchase_timestamp), MAX(order_purchase_timestamp), COUNT(*) FROM orders;
SELECT MIN(order_delivered_customer_date), MAX(order_delivered_customer_date), COUNT(*) FROM orders;
SELECT MIN(order_estimated_delivery_date), MAX(order_estimated_delivery_date), COUNT(*) FROM orders;

SELECT
    order_id,
    order_delivered_customer_date - order_purchase_timestamp AS delivery_time
FROM orders
WHERE order_delivered_customer_date IS NOT NULL;

SELECT
    MIN(order_delivered_customer_date - order_purchase_timestamp) AS min_delivery_time,
	MAX(order_delivered_customer_date - order_purchase_timestamp) AS max_delivery_time,
	AVG(order_delivered_customer_date - order_purchase_timestamp) AS avg_delivery_time
FROM orders
WHERE order_delivered_customer_date IS NOT NULL;

SELECT
    order_id,
    order_status,
    order_purchase_timestamp,
    order_delivered_customer_date,
    order_delivered_customer_date - order_purchase_timestamp AS delivery_time
FROM orders
WHERE order_delivered_customer_date IS NOT NULL
ORDER BY delivery_time DESC
LIMIT 10;

SELECT * FROM orders
	WHERE order_id = 'ca07593549f1816d26a572e06dc1eab6';

SELECT COUNT(*) AS delayed_orders FROM orders
	WHERE order_delivered_customer_date IS NOT NULL
	AND order_delivered_customer_date > order_estimated_delivery_date;

SELECT
    COUNT(*) FILTER (
        WHERE order_delivered_customer_date > order_estimated_delivery_date
    ) * 100.0
    / COUNT(*) AS late_delivery_percentage
FROM orders
WHERE order_status = 'delivered';

SELECT
    DATE_TRUNC('month', order_purchase_timestamp) AS purchase_month,
    COUNT(*) AS total_orders
FROM orders
GROUP BY DATE_TRUNC('month', order_purchase_timestamp)
ORDER BY purchase_month;

SELECT
    DATE_TRUNC('month', order_purchase_timestamp) AS purchase_month,
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (
        WHERE order_status = 'delivered'
    ) AS delivered_orders,
    COUNT(*) FILTER (
        WHERE order_status = 'delivered'
          AND order_delivered_customer_date > order_estimated_delivery_date
    ) AS late_orders,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE order_status = 'delivered'
              AND order_delivered_customer_date > order_estimated_delivery_date
        )
        / NULLIF(
            COUNT(*) FILTER (
                WHERE order_status = 'delivered'
            ),
            0
        ),
        2
    ) AS late_delivery_percentage
FROM orders
GROUP BY DATE_TRUNC('month', order_purchase_timestamp)
ORDER BY purchase_month;