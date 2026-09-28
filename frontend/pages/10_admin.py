"""Admin page: user management (admin only)."""
from __future__ import annotations

import streamlit as st

from utils import api_get

st.title("🔐 Admin Panel")

if not st.session_state.get("token"):
    st.info("Please login to view this page.")
    st.stop()

user = st.session_state.get("user", {})
if user.get("role") != "admin":
    st.error("Admin access required.")
    st.stop()

try:
    data = api_get("/admin/users", params={"page": 1, "page_size": 50})
except Exception as exc:
    st.error(f"Failed to load users: {exc}")
    st.stop()

st.subheader("Users")
for u in data.get("items", []):
    with st.container():
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{u['username']}** — {u['email']} — role: {u['role']}")
        col1.write(f"Active: {u['is_active']} | Verified: {u['is_verified']} | Staff: {u['is_staff']}")