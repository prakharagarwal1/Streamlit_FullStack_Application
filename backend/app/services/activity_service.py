"""Activity log service for audit trail."""
from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import ActivityLog
from app.schemas.activity import ActivityLogResponse


class ActivityService:
    """Record and query user activity logs."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def log(
        self,
        user_id: Optional[int],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        method: Optional[str] = None,
        path: Optional[str] = None,
        status_code: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> ActivityLogResponse:
        entry = ActivityLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            method=method,
            path=path,
            status_code=status_code,
            metadata=metadata,
        )
        self.session.add(entry)
        await self.session.flush()
        await self.session.refresh(entry)
        return ActivityLogResponse.model_validate(entry)

    async def list(
        self,
        page: int = 1,
        page_size: int = 50,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
    ) -> Tuple[List[ActivityLogResponse], int]:
        stmt = select(ActivityLog)
        if user_id is not None:
            stmt = stmt.where(ActivityLog.user_id == user_id)
        if action:
            stmt = stmt.where(ActivityLog.action == action)
        stmt = stmt.order_by(ActivityLog.created_at.desc())
        total_result = await self.session.execute(
            select(ActivityLog).select_from(stmt.subquery())
        )
        total = len(total_result.scalars().all())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(stmt)
        return [ActivityLogResponse.model_validate(a) for a in result.scalars().all()], total