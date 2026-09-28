"""Shared helpers for the Streamlit frontend."""
from __future__ import annotations

import os
from typing import Any, Optional

import httpx


def api_base() -> str:
    return os.getenv("BACKEND_URL", "http://localhost:8000") + "/api/v1"


def _headers() -> dict[str, str]:
    token = st.session_state.get("token")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def api_get(path: str, params: Optional[dict] = None) -> Any:
    """GET from the backend API."""
    with httpx.Client(timeout=30) as client:
        resp = client.get(f"{api_base()}{path}", params=params, headers=_headers())
        resp.raise_for_status()
        return resp.json()


def api_post(path: str, payload: Optional[dict] = None) -> Any:
    """POST to the backend API."""
    with httpx.Client(timeout=30) as client:
        resp = client.post(f"{api_base()}{path}", json=payload or {}, headers=_headers())
        resp.raise_for_status()
        return resp.json() if resp.content else None


def api_put(path: str, payload: Optional[dict] = None) -> Any:
    """PUT to the backend API."""
    with httpx.Client(timeout=30) as client:
        resp = client.put(f"{api_base()}{path}", json=payload or {}, headers=_headers())
        resp.raise_for_status()
        return resp.json() if resp.content else None


def api_patch(path: str, payload: Optional[dict] = None) -> Any:
    """PATCH to the backend API."""
    with httpx.Client(timeout=30) as client:
        resp = client.patch(f"{api_base()}{path}", json=payload or {}, headers=_headers())
        resp.raise_for_status()
        return resp.json() if resp.content else None


def api_delete(path: str) -> Any:
    """DELETE from the backend API."""
    with httpx.Client(timeout=30) as client:
        resp = client.delete(f"{api_base()}{path}", headers=_headers())
        resp.raise_for_status()
        return resp.json() if resp.content else None


def login(email: str, password: str) -> bool:
    """Authenticate and store token + user in session state."""
    try:
        data = api_post("/auth/login", {"email": email, "password": password})
        st.session_state.token = data["access_token"]
        st.session_state.user = data["user"]
        return True
    except httpx.HTTPError as exc:
        st.error(f"Login failed: {exc}")
        return False


def register(username: str, email: str, password: str) -> bool:
    """Register a new user."""
    try:
        data = api_post(
            "/auth/register",
            {"username": username, "email": email, "password": password},
        )
        st.session_state.token = data["access_token"]
        st.session_state.user = data["user"]
        return True
    except httpx.HTTPError as exc:
        st.error(f"Registration failed: {exc}")
        return False


import streamlit as st  # noqa: E402