"""Files page: upload, list, delete."""
from __future__ import annotations

import streamlit as st

from utils import api_delete, api_get, api_post

st.title("📁 Files")

if not st.session_state.get("token"):
    st.info("Please login to view this page.")
    st.stop()

# --- Upload -----------------------------------------------------------------
with st.expander("⬆️ Upload File"):
    with st.form("upload"):
        file = st.file_uploader("Choose a file")
        is_public = st.checkbox("Public")
        expires = st.number_input("Expires in days (0 = never)", min_value=0, value=0)
        if st.form_submit_button("Upload") and file:
            try:
                import httpx

                with httpx.Client(timeout=60) as client:
                    resp = client.post(
                        f"{st.session_state.api_base}/files",
                        files={"file": (file.name, file, file.type)},
                        data={
                            "is_public": str(is_public).lower(),
                            "expires_in_days": str(expires) if expires > 0 else "",
                        },
                        headers={"Authorization": f"Bearer {st.session_state.token}"},
                    )
                    resp.raise_for_status()
                st.success("Uploaded!")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

# --- List files -------------------------------------------------------------
try:
    data = api_get("/files", params={"page": 1, "page_size": 20})
except Exception as exc:
    st.error(f"Failed to load files: {exc}")
    st.stop()

for f in data.get("items", []):
    with st.container():
        col1, col2 = st.columns([4, 1])
        col1.write(f"{f['original_filename']} — {f['size_bytes']} bytes — {f['category']}")
        if col2.button("Delete", key=f"del_file_{f['id']}"):
            try:
                api_delete(f"/files/{f['id']}")
                st.success("Deleted")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))