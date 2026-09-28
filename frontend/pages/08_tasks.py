"""Tasks page: create, list, update, delete background tasks."""
from __future__ import annotations

import streamlit as st

from utils import api_delete, api_get, api_post, api_patch

st.title("✅ Tasks")

if not st.session_state.get("token"):
    st.info("Please login to view this page.")
    st.stop()

# --- Create task ------------------------------------------------------------
with st.expander("➕ Create Task"):
    with st.form("create_task"):
        name = st.text_input("Name *")
        description = st.text_area("Description")
        priority = st.selectbox("Priority", ["low", "medium", "high", "critical"])
        queue = st.text_input("Queue", value="default")
        if st.form_submit_button("Create"):
            try:
                api_post(
                    "/tasks",
                    {"name": name, "description": description or None, "priority": priority, "queue": queue},
                )
                st.success("Task created!")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

# --- List tasks -------------------------------------------------------------
try:
    data = api_get("/tasks", params={"page": 1, "page_size": 20})
except Exception as exc:
    st.error(f"Failed to load tasks: {exc}")
    st.stop()

for task in data.get("items", []):
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.subheader(task["name"])
        col1.write(f"Status: {task['status']} | Priority: {task['priority']} | Progress: {task['progress']}%")
        if task.get("error_message"):
            col1.error(task["error_message"])
        new_status = col2.selectbox(
            "Status",
            ["pending", "running", "success", "failed", "retry"],
            index=["pending", "running", "success", "failed", "retry"].index(task["status"]),
            key=f"status_{task['id']}",
        )
        if col3.button("Update", key=f"update_{task['id']}"):
            try:
                api_patch(f"/tasks/{task['id']}", {"status": new_status})
                st.rerun()
            except Exception as exc:
                st.error(str(exc))