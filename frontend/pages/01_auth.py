"""Authentication page: login + register."""
from __future__ import annotations

import streamlit as st

from utils import login, register

st.title("🔐 Authentication")

tab_login, tab_register = st.tabs(["Login", "Register"])

with tab_login:
    st.subheader("Welcome back")
    with st.form("login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Login", use_container_width=True)
        if submitted:
            if not email or not password:
                st.warning("Please fill in all fields.")
            elif login(email, password):
                st.success("Logged in!")
                st.rerun()

with tab_register:
    st.subheader("Create an account")
    with st.form("register_form"):
        username = st.text_input("Username", key="reg_username")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password (min 8 chars)", type="password", key="reg_password")
        submitted = st.form_submit_button("Register", use_container_width=True)
        if submitted:
            if not username or not email or not password:
                st.warning("Please fill in all fields.")
            elif len(password) < 8:
                st.warning("Password must be at least 8 characters.")
            elif register(username, email, password):
                st.success("Account created!")
                st.rerun()