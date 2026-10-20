import pandas as pd

from src.ingest import load_orders, load_order_item_features


def build_dataset() -> pd.DataFrame:
    orders = load_orders()
    item_features = load_order_item_features()

    df = orders.merge(
        item_features,
        on="order_id",
        how="left",
    )

    df = df[
        (df["order_status"] == "delivered")
        & df["order_delivered_customer_date"].notna()
        & df["order_estimated_delivery_date"].notna()
    ].copy()

    df["is_late"] = (
        df["order_delivered_customer_date"]
        > df["order_estimated_delivery_date"]
    ).astype(int)

    return df

def prepare_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    df = df.copy()

    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"]
    )
    df["order_estimated_delivery_date"] = pd.to_datetime(
        df["order_estimated_delivery_date"]
    )

    df["purchase_month"] = df["order_purchase_timestamp"].dt.month
    df["purchase_day_of_week"] = df["order_purchase_timestamp"].dt.dayofweek
    df["purchase_hour"] = df["order_purchase_timestamp"].dt.hour

    df["estimated_delivery_days"] = (
        df["order_estimated_delivery_date"]
        - df["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400

    feature_columns = [
        "item_count",
        "total_price",
        "total_freight",
        "seller_count",
        "purchase_month",
        "purchase_day_of_week",
        "purchase_hour",
        "estimated_delivery_days",
    ]

    X = df[feature_columns].copy()
    y = df["is_late"].copy()

    return X, y