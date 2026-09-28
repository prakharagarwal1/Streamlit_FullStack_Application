"""AI summarization task (OpenAI-backed, optional)."""
from __future__ import annotations

from typing import Any

from app.config import get_settings
from app.tasks.worker import app

settings = get_settings()


@app.task(name="app.tasks.summarize_text", bind=True, max_retries=2)
def summarize_text_task(self, text: str, **kwargs: Any) -> dict:
    """Summarize text using OpenAI (if API key configured)."""
    if not settings.OPENAI_API_KEY:
        return {"summary": text[:200], "status": "fallback_truncated"}
    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Summarize the following text."},
                {"role": "user", "content": text},
            ],
        )
        summary = resp.choices[0].message.content
        return {"summary": summary, "status": "completed"}
    except Exception as exc:  # pragma: no cover - network path
        return {"summary": text[:200], "status": "error", "error": str(exc)}