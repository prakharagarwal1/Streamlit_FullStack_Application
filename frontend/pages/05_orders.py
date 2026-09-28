"""Orders page: create, list, cancel."""
from __future__ import annotations

import streamlit as st

from utils import api_delete, api_get, api_post

st.title("🧾 Orders")

if not st.session_state.get("token"):
    st.info("Please login to view this page.")
    st.stop()

user_id = st.session_state.get("user", {}).get("id")

# --- Create order -----------------------------------------------------------
with st.expander("➕ Create Order"):
    with st.form("create_order"):
        product_id = st.number_input("Product ID", min_value=1, value=1)
        quantity = st.number_input("Quantity", min_value=1, value=1)
        shipping = st.text_area("Shipping address")
        if st.form_submit_button("Create Order"):
            try:
                api_post(
                    "/orders",
                    {
                        "items": [{"product_id": int(product_id), "quantity": int(quantity)}],
                        "shipping_address": shipping or None,
                    },
                )
                st.success("Order created!")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

# --- List orders ------------------------------------------------------------
try:
    data = api_get("/orders", params={"page": 1, "page_size": 20})
except Exception as exc:
    st.error(f"Failed to load orders: {exc}")
    st.stop()

for order in data.get("items", []):
    with st.container():
        col1, col2 = st.columns([4, 1])
        col1.subheader(f"Order #{order['order_number']}")
        col1.write(f"Status: {order['status']} | Total: ${order['total_amount']:.2f}")
        for item in order.get("items", []):
            col1.write(f"  - Product {item['product_id']} x{item['quantity']} @ ${item['unit_price']:.2f}")
        if col2.button("Cancel", key=f"cancel_{order['id']}"):
            try:
                api_post(f"/orders/{order['id']}/cancel")
                st.success("Cancelled")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))