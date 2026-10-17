
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