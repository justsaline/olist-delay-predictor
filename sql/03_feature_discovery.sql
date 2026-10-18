SELECT * FROM order_items LIMIT 5;

SELECT order_id, COUNT(*) AS items_per_order FROM order_items
	GROUP BY order_id;

SELECT AVG(order_item_id) AS avg_items_per_order FROM order_items;

SELECT order_id, COUNT(*) AS items_per_order FROM order_items
	GROUP BY order_id
	ORDER BY items_per_order DESC;

SELECT MAX(order_item_id) FROM order_items;

SELECT COUNT(*) AS items_more_than1 FROM order_items
	WHERE order_item_id > 1;

SELECT MIN(price) AS min_price, MAX(price) AS max_price, AVG(price) AS avg_price FROM order_items;

SELECT order_id, AVG(price) as avg_item_price FROM order_items
	GROUP BY order_id;