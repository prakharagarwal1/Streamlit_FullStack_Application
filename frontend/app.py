"""Streamlit FullStack Demo — multi-page app entry point."""
from __future__ import annotations

import os
import streamlit as st

# --- Page config ------------------------------------------------------------
st.set_page_config(
    page_title=os.getenv("APP_NAME", "Streamlit FullStack Demo"),
    page_icon=os.getenv("PAGE_ICON", "🚀"),
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Session state defaults -------------------------------------------------
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "api_base" not in st.session_state:
    st.session_state.api_base = os.getenv("BACKEND_URL", "http://localhost:8000") + "/api/v1"


# --- Sidebar ----------------------------------------------------------------
with st.sidebar:
    st.title("🚀 FullStack Demo")
    st.markdown("---")
    if st.session_state.user:
        st.success(f"Logged in as **{st.session_state.user.get('username')}**")
        if st.button("Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()
    else:
        st.info("Please login to access the dashboard.")
    st.markdown("---")
    st.markdown(
        "Pages: **Auth** · **Dashboard** · **Charts** · **Products** · "
        "**Orders** · **Blog** · **Files** · **Tasks** · **AI** · **Admin**"
    )