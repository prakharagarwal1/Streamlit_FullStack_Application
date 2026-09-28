"""Blog page: posts + tags."""
from __future__ import annotations

import streamlit as st

from utils import api_delete, api_get, api_post, api_put

st.title("📝 Blog")

if not st.session_state.get("token"):
    st.info("Please login to view this page.")
    st.stop()

# --- Create post ------------------------------------------------------------
with st.expander("➕ Write a Post"):
    with st.form("create_post"):
        title = st.text_input("Title *")
        content = st.text_area("Content *")
        excerpt = st.text_area("Excerpt")
        status = st.selectbox("Status", ["draft", "published"])
        tag_ids = st.text_input("Tag IDs (comma-separated)")
        if st.form_submit_button("Publish"):
            try:
                tags = [int(t.strip()) for t in tag_ids.split(",") if t.strip()]
                api_post(
                    "/posts",
                    {
                        "title": title,
                        "content": content,
                        "excerpt": excerpt or None,
                        "status": status,
                        "tag_ids": tags,
                    },
                )
                st.success("Post created!")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

# --- List posts -------------------------------------------------------------
try:
    data = api_get("/posts", params={"page": 1, "page_size": 20})
except Exception as exc:
    st.error(f"Failed to load posts: {exc}")
    st.stop()

for post in data.get("items", []):
    with st.container():
        col1, col2 = st.columns([4, 1])
        col1.subheader(post["title"])
        col1.write(post.get("excerpt") or post["content"][:200])
        col1.write(f"Status: {post['status']} | Views: {post['view_count']}")
        tags = ", ".join(t["name"] for t in post.get("tags", []))
        if tags:
            col1.write(f"Tags: {tags}")
        if col2.button("Delete", key=f"del_post_{post['id']}"):
            try:
                api_delete(f"/posts/{post['id']}")
                st.success("Deleted")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))