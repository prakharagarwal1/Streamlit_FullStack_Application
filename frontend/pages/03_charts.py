"""Charts page: demonstrates Plotly, Matplotlib, Seaborn, WordCloud, ECharts."""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

st.title("📈 Charts Library Showcase")

if not st.session_state.get("token"):
    st.info("Please login to view this page.")
    st.stop()

# --- Plotly -----------------------------------------------------------------
st.subheader("1. Plotly — Interactive Line + Bar")
import plotly.express as px

df = pd.DataFrame(
    {
        "date": pd.date_range("2026-09-01", periods=10),
        "sales": np.random.randint(50, 200, 10).cumsum(),
        "target": np.linspace(100, 1000, 10),
    }
)
fig_line = px.line(df, x="date", y=["sales", "target"], title="Sales vs Target")
st.plotly_chart(fig_line, use_container_width=True)

fig_pie = px.pie(
    names=["A", "B", "C", "D"], values=[40, 30, 20, 10], title="Market Share"
)
st.plotly_chart(fig_pie, use_container_width=True)

# --- Matplotlib -------------------------------------------------------------
st.subheader("2. Matplotlib — Histogram + Scatter")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].hist(np.random.randn(500), bins=40, color="steelblue")
axes[0].set_title("Histogram")
x = np.random.randn(100)
y = x * 0.5 + np.random.randn(100) * 0.3
axes[1].scatter(x, y, alpha=0.6, color="coral")
axes[1].set_title("Scatter")
st.pyplot(fig)

# --- Seaborn ----------------------------------------------------------------
st.subheader("3. Seaborn — Heatmap + Boxplot")
import seaborn as sns

tips = sns.load_dataset("tips")
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
sns.heatmap(tips.select_dtypes(include="number").corr(), annot=True, ax=axes[0])
sns.boxplot(data=tips, x="day", y="total_bill", ax=axes[1])
st.pyplot(fig)

# --- WordCloud --------------------------------------------------------------
st.subheader("4. WordCloud")
from wordcloud import WordCloud

text = (
    "streamlit fastapi python fullstack backend frontend charts data "
    "machine learning ai docker deployment cloud database api"
)
wc = WordCloud(width=800, height=400, background_color="white").generate(text)
fig, ax = plt.subplots(figsize=(10, 5))
ax.imshow(wc, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig)

# --- ECharts (via streamlit-echarts) ----------------------------------------
st.subheader("5. ECharts — Bar chart")
try:
    from streamlit_echarts import st_echarts

    option = {
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": ["Mon", "Tue", "Wed", "Thu", "Fri"]},
        "yAxis": {"type": "value"},
        "series": [
            {"name": "Sales", "type": "bar", "data": [120, 200, 150, 180, 220]}
        ],
    }
    st_echarts(option, height="400px")
except Exception as exc:
    st.info(f"streamlit-echarts not available: {exc}")

# --- Pandas DataFrame Explorer ---------------------------------------------
st.subheader("6. Pandas + Streamlit AgGrid")
try:
    from st_aggrid import AgGrid, GridOptionsBuilder

    dfx = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie", "Diana"],
            "age": [25, 30, 35, 28],
            "city": ["NYC", "LA", "Chicago", "Seattle"],
        }
    )
    gb = GridOptionsBuilder.from_dataframe(dfx)
    gb.configure_pagination()
    gb.configure_side_bar()
    grid = AgGrid(dfx, gridOptions=gb.build(), height=200)
except Exception as exc:
    st.dataframe(dfx, use_container_width=True)
    st.info(f"AgGrid not available: {exc}")