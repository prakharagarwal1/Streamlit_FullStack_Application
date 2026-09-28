"""Serialization helpers."""
from __future__ import annotations

from datetime import datetime
from typing import Any


def to_dict(obj: Any) -> dict:
    """Convert an object (e.g. SQLAlchemy model) to a plain dict."""
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in vars(obj).items() if not k.startswith("_")}
    if isinstance(obj, dict):
        return dict(obj)
    return {"value": obj}


def model_to_dict(obj: Any) -> dict:
    """Convert a SQLAlchemy model instance to a JSON-serializable dict."""
    result = to_dict(obj)
    for key, value in list(result.items()):
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        elif hasattr(value, "__dict__") and not isinstance(value, (str, int, float, bool)):
            result[key] = model_to_dict(value)
    return result