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