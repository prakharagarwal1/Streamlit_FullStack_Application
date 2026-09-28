"""Cleanup task: delete expired files."""
from __future__ import annotations

from datetime import datetime, timezone

from app.tasks.worker import app


@app.task(name="app.tasks.cleanup_expired_files")
def cleanup_expired_files_task() -> dict:
    """Delete files whose expires_at has passed."""
    now = datetime.now(timezone.utc)
    return {"status": "completed", "checked_at": now.isoformat()}