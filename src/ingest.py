
import pandas as pd
from sqlalchemy import text

from src.db import engine


def load_orders() -> pd.DataFrame:
    query = text("""
        SELECT *
        FROM orders
    """)

    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    return df

def load_order_item_features() -> pd.DataFrame:
    query = text("""
        SELECT
            order_id,
            COUNT(*) AS item_count,
            SUM(price) AS total_price,
            SUM(freight_value) AS total_freight,
            COUNT(DISTINCT seller_id) AS seller_count
        FROM order_items
        GROUP BY order_id
    """)

    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    return df