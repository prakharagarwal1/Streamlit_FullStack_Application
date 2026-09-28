"""Email task (stub)."""
from __future__ import annotations

from typing import Any

from app.tasks.worker import app


@app.task(name="app.tasks.send_email", bind=True, max_retries=3)
def send_email_task(self, to: str, subject: str, body: str, **kwargs: Any) -> dict:
    """Send an email (stub — logs instead of SMTP)."""
    print(f"[email] To: {to} | Subject: {subject}")
    return {"to": to, "subject": subject, "status": "sent"}