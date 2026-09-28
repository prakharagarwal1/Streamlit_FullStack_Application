"""Products page: list, filter, create, update, delete."""
from __future__ import annotations

import streamlit as st

from utils import api_delete, api_get, api_post, api_put

st.title("🛒 Products")

if not st.session_state.get("token"):
    st.info("Please login to view this page.")
    st.stop()

# --- Filters ----------------------------------------------------------------
with st.expander("🔍 Filters", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    search = c1.text_input("Search")
    category_id = c2.number_input("Category ID", min_value=0, value=0)
    is_active = c3.selectbox("Active", ["All", "Yes", "No"])
    page = c4.number_input("Page", min_value=1, value=1)

params = {"page": page, "page_size": 20}
if search:
    params["search"] = search
if category_id > 0:
    params["category_id"] = category_id
if is_active == "Yes":
    params["is_active"] = True
elif is_active == "No":
    params["is_active"] = False

try:
    data = api_get("/products", params=params)
except Exception as exc:
    st.error(f"Failed to load products: {exc}")
    st.stop()

items = data.get("items", [])
st.write(f"Showing {len(items)} of {data.get('total', 0)} products")

for product in items:
    with st.container():
        col1, col2 = st.columns([3, 1])
        col1.subheader(product["name"])
        col1.write(f"SKU: {product.get('sku')} | Category: {product.get('category_id')}")
        col1.write(product.get("description") or "")
        col1.write(f"Price: ${product['price']:.2f} | Stock: {product['stock_quantity']}")
        if product.get("is_low_stock"):
            col1.warning("⚠️ Low stock!")
        if col2.button("Delete", key=f"del_{product['id']}"):
            try:
                api_delete(f"/products/{product['id']}")
                st.success("Deleted")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

# --- Create form ------------------------------------------------------------
with st.expander("➕ Add Product"):
    with st.form("create_product"):
        name = st.text_input("Name *")
        slug = st.text_input("Slug")
        sku = st.text_input("SKU")
        price = st.number_input("Price", min_value=0.0, step=0.01)
        stock = st.number_input("Stock", min_value=0, step=1)
        category_id = st.number_input("Category ID", min_value=0, step=1)
        description = st.text_area("Description")
        if st.form_submit_button("Create"):
            try:
                api_post(
                    "/products",
                    {
                        "name": name,
                        "slug": slug or None,
                        "sku": sku or None,
                        "price": price,
                        "stock_quantity": stock,
                        "category_id": category_id or None,
                        "description": description or None,
                    },
                )
                st.success("Created!")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))