"""HTTP client helpers."""
from __future__ import annotations

from typing import Any, Optional

import httpx


async def http_get(url: str, params: Optional[dict] = None, headers: Optional[dict] = None) -> Any:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url, params=params, headers=headers or {})
        response.raise_for_status()
        return response.json()


async def http_post(url: str, json: Optional[dict] = None, headers: Optional[dict] = None) -> Any:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, json=json, headers=headers or {})
        response.raise_for_status()
        return response.json()