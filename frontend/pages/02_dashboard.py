"""Dashboard page: overview + charts."""
from __future__ import annotations

import streamlit as st

from utils import api_get

st.title("📊 Dashboard")

if not st.session_state.get("token"):
    st.info("Please login to view the dashboard.")
    st.stop()

try:
    overview = api_get("/analytics/overview")
except Exception as exc:
    st.error(f"Failed to load overview: {exc}")
    st.stop()

# --- KPIs -------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Users", overview.get("total_users", 0))
c2.metric("Total Products", overview.get("total_products", 0))
c3.metric("Total Orders", overview.get("total_orders", 0))
c4.metric("Total Revenue", f"${overview.get('total_revenue', 0):,.2f}")

st.markdown("---")

# --- Sales last 7 days ------------------------------------------------------
try:
    sales = api_get("/analytics/sales-last-7-days")
    import pandas as pd

    df = pd.DataFrame(sales)
    if not df.empty:
        st.subheader("Sales Last 7 Days")
        st.line_chart(df.set_index("date")["revenue"])
except Exception as exc:
    st.warning(f"Sales chart unavailable: {exc}")

# --- Top products -----------------------------------------------------------
try:
    top = api_get("/analytics/top-products", params={"limit": 5})
    if top:
        import pandas as pd

        dfp = pd.DataFrame(top)
        st.subheader("Top Products by Price")
        st.bar_chart(dfp.set_index("name")["price"])
except Exception as exc:
    st.warning(f"Top products unavailable: {exc}")