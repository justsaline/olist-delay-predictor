import requests
import streamlit as st

st.set_page_config(
    page_title="Olist Delivery Delay Predictor",
    layout="wide",
)

BRAZIL_STATES = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]

DAYS_OF_WEEK = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}

st.title("Olist Delivery Delay Predictor")
st.caption(
    "Predicts late-delivery risk at order checkout using a regularized XGBoost pipeline served via FastAPI."
)

with st.sidebar:
    st.header("API & Threshold Settings")
    api_url = st.text_input("FastAPI Base URL", value="http://localhost:8000", key="api_url")

    try:
        health = requests.get(f"{api_url}/health", timeout=2).json()
        st.success(f"API Online (default cutoff: {health.get('default_threshold', 0.70)})")
    except requests.RequestException:
        st.error("API Offline — start `uvicorn src.api:app --reload`")

    threshold = st.slider(
        "Decision Threshold",
        min_value=0.10,
        max_value=0.95,
        value=0.70,
        step=0.05,
        key="threshold_slider",
        help="Lower values catch more delays (higher recall); higher values reduce false alarms (higher precision).",
    )
    st.markdown(
        "**Validation benchmarks (XGBoost):**\n"
        "- `0.65`: 21.2% precision | 43.7% recall\n"
        "- `0.70`: 25.5% precision | 30.5% recall *(default)*\n"
        "- `0.75`: 30.2% precision | 14.5% recall"
    )

with st.form("order_prediction_form"):
    col_route, col_order = st.columns(2)

    with col_route:
        st.subheader("Route & Delivery Window")
        seller_state = st.selectbox(
            "Seller State",
            options=BRAZIL_STATES,
            index=BRAZIL_STATES.index("SP"),
            key="seller_state",
        )
        customer_state = st.selectbox(
            "Customer State",
            options=BRAZIL_STATES,
            index=BRAZIL_STATES.index("RJ"),
            key="customer_state",
        )
        zip_prefix_diff = st.number_input(
            "Zip Code Prefix Difference",
            min_value=0.0,
            max_value=99999.0,
            value=15000.0,
            step=500.0,
            key="zip_prefix_diff",
            help="Absolute difference between customer and seller 5-digit CEP prefixes.",
        )
        estimated_delivery_days = st.number_input(
            "Promised Delivery Window (days)",
            min_value=1.0,
            max_value=120.0,
            value=18.0,
            step=1.0,
            key="estimated_delivery_days",
        )
        day_name = st.selectbox(
            "Purchase Day of Week",
            options=list(DAYS_OF_WEEK.keys()),
            index=2,
            key="purchase_day",
        )
        purchase_hour = st.slider(
            "Purchase Hour (24h)",
            min_value=0,
            max_value=23,
            value=14,
            key="purchase_hour",
        )

    with col_order:
        st.subheader("Order & Package Specs")
        item_count = st.number_input(
            "Item Count",
            min_value=1,
            max_value=50,
            value=1,
            step=1,
            key="item_count",
        )
        seller_count = st.number_input(
            "Distinct Sellers",
            min_value=1,
            max_value=20,
            value=1,
            step=1,
            key="seller_count",
        )
        total_price = st.number_input(
            "Total Item Price (BRL)",
            min_value=0.0,
            value=120.0,
            step=10.0,
            key="total_price",
        )
        total_freight = st.number_input(
            "Total Freight Cost (BRL)",
            min_value=0.0,
            value=22.5,
            step=2.5,
            key="total_freight",
        )
        total_weight_g = st.number_input(
            "Total Package Weight (g)",
            min_value=0.0,
            value=800.0,
            step=100.0,
            key="total_weight_g",
        )
        total_volume_cm3 = st.number_input(
            "Total Box Volume (cm³)",
            min_value=0.0,
            value=4500.0,
            step=500.0,
            key="total_volume_cm3",
        )

    submitted = st.form_submit_button("Predict Delay Risk", type="primary", use_container_width=True)

if submitted:
    payload = {
        "item_count": int(item_count),
        "total_price": float(total_price),
        "total_freight": float(total_freight),
        "seller_count": int(seller_count),
        "total_weight_g": float(total_weight_g),
        "total_volume_cm3": float(total_volume_cm3),
        "zip_prefix_diff": float(zip_prefix_diff),
        "purchase_day_of_week": DAYS_OF_WEEK[day_name],
        "purchase_hour": int(purchase_hour),
        "estimated_delivery_days": float(estimated_delivery_days),
        "customer_state": customer_state,
        "seller_state": seller_state,
        "threshold": float(threshold),
    }

    try:
        response = requests.post(f"{api_url}/predict", json=payload, timeout=5)
        response.raise_for_status()
        result = response.json()

        prob = result["delay_probability"]
        is_late = result["predicted_late"]
        is_interstate = result["is_interstate"]

        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Delay Probability", f"{prob * 100:.1f}%")
        m2.metric("Operating Threshold", f"{result['threshold_used'] * 100:.0f}%")
        m3.metric("Shipment Route", "Interstate" if is_interstate else "Intrastate (Local)")

        st.progress(min(max(prob, 0.0), 1.0))

        if is_late:
            st.error(
                f"High Delay Risk ({prob * 100:.1f}% >= {threshold * 100:.0f}% threshold) — "
                "Recommend padding customer-facing ETA by 2–3 days or flagging for carrier tracking."
            )
        else:
            st.success(
                f"On-Time Expected ({prob * 100:.1f}% < {threshold * 100:.0f}% threshold) — "
                "Standard promised delivery window holds."
            )

        with st.expander("Inspect Request & API Response JSON"):
            c1, c2 = st.columns(2)
            c1.json(payload)
            c2.json(result)

    except requests.exceptions.ConnectionError:
        st.error("Could not connect to FastAPI. Make sure `uvicorn src.api:app --reload` is running.")
    except requests.HTTPError as exc:
        st.error(f"API returned an error: {exc.response.status_code} — {exc.response.text}")