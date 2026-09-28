"""Report generation task."""
from __future__ import annotations

import io
from typing import Any

from app.tasks.worker import app


@app.task(name="app.tasks.generate_report", bind=True, max_retries=2)
def generate_report_task(self, report_type: str = "sales", **kwargs: Any) -> dict:
    """Generate a CSV/PDF report (stub)."""
    import csv

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["report_type", report_type])
    writer.writerow(["generated_at", "2026-09-28T00:00:00Z"])
    writer.writerow(["status", "completed"])
    return {"report_type": report_type, "csv": buf.getvalue()}