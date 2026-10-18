SELECT * FROM order_items LIMIT 5;

SELECT order_id, COUNT(*) AS items_per_order FROM order_items
	GROUP BY order_id;

SELECT AVG(items_per_order) AS avg_items_per_order
FROM (
    SELECT order_id, COUNT(*) AS items_per_order
    FROM order_items
    GROUP BY order_id
) AS order_counts;

SELECT order_id, COUNT(*) AS items_per_order FROM order_items
	GROUP BY order_id
	ORDER BY items_per_order DESC;

SELECT MAX(order_item_id) FROM order_items;

SELECT COUNT(*) AS items_more_than1 FROM order_items
	WHERE order_item_id > 1;

SELECT MIN(price) AS min_price, MAX(price) AS max_price, AVG(price) AS avg_price FROM order_items;

SELECT order_id, AVG(price) as avg_item_price FROM order_items
	GROUP BY order_id;

SELECT order_id, COUNT(*) AS item_count, SUM(price) AS total_price, 
	SUM(freight_value) AS total_freight
	FROM order_items
	GROUP BY order_id;

SELECT
    order_id,
    COUNT(DISTINCT seller_id) AS seller_count
	FROM order_items
	GROUP BY order_id;

SELECT
    oi.order_id,
    oi.order_item_id,
    oi.shipping_limit_date,
    o.order_purchase_timestamp,
    EXTRACT(
        EPOCH FROM (oi.shipping_limit_date - o.order_purchase_timestamp)
    ) / 3600 AS hours_until_shipping_limit
	FROM order_items oi
	JOIN orders o
    	ON oi.order_id = o.order_id
	ORDER BY hours_until_shipping_limit;

SELECT
    order_id,
    SUM(price) AS total_price,
    SUM(freight_value) AS total_freight,
    ROUND(
        (SUM(freight_value) / NULLIF(SUM(price), 0))::numeric,
        3
    ) AS freight_to_price_ratio
	FROM order_items
	GROUP BY order_id
	ORDER BY freight_to_price_ratio DESC NULLS LAST;