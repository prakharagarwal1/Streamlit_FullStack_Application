"""AI page: text summarization + image generation."""
from __future__ import annotations

import os

import streamlit as st

from utils import api_post

st.title("🤖 AI Features")

if not st.session_state.get("token"):
    st.info("Please login to view this page.")
    st.stop()

# --- Text summarization -----------------------------------------------------
st.subheader("Text Summarization")
text = st.text_area("Paste text to summarize", height=200)
if st.button("Summarize") and text:
    try:
        result = api_post("/tasks", {"name": "summarize", "kwargs": {"text": text}})
        st.write("Task queued:", result.get("id"))
    except Exception as exc:
        st.error(str(exc))

# --- Image generation -------------------------------------------------------
st.subheader("Image Generation (DALL·E / Stable Diffusion)")
prompt = st.text_input("Prompt")
if st.button("Generate Image") and prompt:
    try:
        import httpx

        with httpx.Client(timeout=120) as client:
            resp = client.post(
                f"{st.session_state.api_base}/files/upload-image",
                json={"prompt": prompt},
                headers={"Authorization": f"Bearer {st.session_state.token}"},
            )
            resp.raise_for_status()
        st.image(resp.content)
    except Exception as exc:
        st.info(f"Image generation not configured: {exc}")

st.markdown("---")
st.info("Set OPENAI_API_KEY in the backend .env to enable AI features.")