import pandas as pd
from sqlalchemy import text
from src.db import engine

def load_orders():
    query = text("""SELECT * FROM orders""")
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)
    return df

if __name__ == "__main__":
    orders = load_orders()
    print("Shape:", orders.shape)
    print("\nFirst 5 rows:")
    print(orders.head())

    print("\nData types:")
    print(orders.dtypes)

    print("\nMissing values:")
    print(orders.isnull().sum())

    print("\nOrder status distribution:")
    print(orders["order_status"].value_counts())

    print("\nDelivery timestamp availability by status:")

    print(
        orders.groupby("order_status")[
            "order_delivered_customer_date"
        ].agg(
            total_orders="size",
            missing_delivery_dates=lambda s: s.isna().sum(),
        )
    )