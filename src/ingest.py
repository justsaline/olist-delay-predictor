import pandas as pd
from sqlalchemy import text

from src.db import engine


def load_orders() -> pd.DataFrame:
    query = text("""
        SELECT
            o.*,
            c.customer_state,
            c.customer_zip_code_prefix
        FROM orders o
        LEFT JOIN customers c
            ON o.customer_id = c.customer_id
    """)

    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    return df


def load_order_item_features() -> pd.DataFrame:
    query = text("""
        SELECT
            oi.order_id,
            COUNT(*) AS item_count,
            SUM(oi.price) AS total_price,
            SUM(oi.freight_value) AS total_freight,
            COUNT(DISTINCT oi.seller_id) AS seller_count,
            SUM(COALESCE(p.product_weight_g, 0)) AS total_weight_g,
            SUM(
                COALESCE(
                    CAST(p.product_length_cm AS BIGINT)
                    * p.product_height_cm
                    * p.product_width_cm,
                    0
                )
            ) AS total_volume_cm3,
            MAX(s.seller_state) AS seller_state,
            MAX(s.seller_zip_code_prefix) AS seller_zip_code_prefix
        FROM order_items oi
        LEFT JOIN products p
            ON oi.product_id = p.product_id
        LEFT JOIN sellers s
            ON oi.seller_id = s.seller_id
        GROUP BY oi.order_id
    """)

    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    return df