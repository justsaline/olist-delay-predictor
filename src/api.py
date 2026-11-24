from pathlib import Path
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

ARTIFACT_PATH = Path("models/xgb_delay_predictor.joblib")
artifact = joblib.load(ARTIFACT_PATH)

model = artifact["model"]
DEFAULT_THRESHOLD = float(artifact["threshold"])
FEATURE_COLUMNS = artifact["feature_columns"]

app = FastAPI(
    title = "Olist Delivery Delay Predictor",
    description = "Predicts whether an Olist order will arrive after its estimated delivery date.",
    version = "1.0.0",
)

class OrderRequest(BaseModel):
    item_count: int = Field(1, ge=1, description="Number of items in the order")
    total_price: float = Field(120.0, ge=0, description="Total item price in BRL")
    total_freight: float = Field(22.5, ge=0, description="Total freight cost in BRL")
    seller_count: int = Field(1, ge=1, description="Number of distinct sellers")
    total_weight_g: float = Field(800.0, ge=0, description="Total package weight in grams")
    total_volume_cm3: float = Field(4500.0, ge=0, description="Total package box volume in cm³")
    zip_prefix_diff: float = Field(15000.0, ge=0, description="Absolute difference between customer and seller zip prefixes")
    purchase_day_of_week: int = Field(2, ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    purchase_hour: int = Field(14, ge=0, le=23, description="Hour of purchase (0-23)")
    estimated_delivery_days: float = Field(18.0, gt=0, description="Promised delivery window in days")
    customer_state: str = Field("RJ", min_length=2, max_length=2, description="2-letter customer state code")
    seller_state: str = Field("SP", min_length=2, max_length=2, description="2-letter seller state code")
    threshold: float = Field(
        default=DEFAULT_THRESHOLD,
        ge=0.0,
        le=1.0,
        description="Probability cutoff (defaults to saved 0.70 threshold)",
    )

@app.get("/")
def root():
    return {
        "message": "Olist Delivery Delay Predictor API is running",
        "docs": "/docs",
        "health": "/health",
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "default_threshold": DEFAULT_THRESHOLD,
        "features_expected":len(FEATURE_COLUMNS)
    }

@app.post("/predict")
def predict_delay(order: OrderRequest):
    customer_state = order.customer_state.strip().upper()
    seller_state = order.seller_state.strip().upper()
    is_interstate = int(seller_state != customer_state)

    row = {
        "item_count": order.item_count,
        "total_price": order.total_price,
        "total_freight": order.total_freight,
        "seller_count": order.seller_count,
        "total_weight_g": order.total_weight_g,
        "total_volume_cm3": order.total_volume_cm3,
        "is_interstate": is_interstate,
        "zip_prefix_diff": order.zip_prefix_diff,
        "purchase_day_of_week": order.purchase_day_of_week,
        "purchase_hour": order.purchase_hour,
        "estimated_delivery_days": order.estimated_delivery_days,
        "customer_state": customer_state,
        "seller_state": seller_state,
    }

    input_df = pd.DataFrame([row])[FEATURE_COLUMNS]
    delay_probability = float(model.predict_proba(input_df)[:,-1][0])

    threshold = order.threshold if order.threshold is not None else DEFAULT_THRESHOLD
    is_late = delay_probability >= threshold

    return {
        "delay_probability": round(delay_probability, 4),
        "threshold_used": threshold,
        "predicted_late": is_late,
        "is_interstate": bool(is_interstate),
    }