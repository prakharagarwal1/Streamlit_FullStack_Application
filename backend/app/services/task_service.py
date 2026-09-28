"""Task service: manage background tasks in DB."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate


class TaskService:
    """Track background tasks in the database."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_task(
        self, payload: TaskCreate, user_id: Optional[int] = None
    ) -> TaskResponse:
        scheduled_at = None
        if payload.scheduled_at:
            try:
                scheduled_at = datetime.fromisoformat(payload.scheduled_at)
            except ValueError:
                scheduled_at = None
        task = Task(
            name=payload.name,
            description=payload.description,
            user_id=user_id,
            priority=payload.priority,
            queue=payload.queue,
            args=payload.args,
            kwargs=payload.kwargs,
            scheduled_at=scheduled_at,
        )
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)
        return TaskResponse.model_validate(task)

    async def get_task(self, task_id: int) -> TaskResponse:
        result = await self.session.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            raise NotFoundError("Task not found")
        return TaskResponse.model_validate(task)

    async def update_task(self, task_id: int, payload: TaskUpdate) -> TaskResponse:
        result = await self.session.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            raise NotFoundError("Task not found")
        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(task, field, value)
        if task.status == "running" and task.started_at is None:
            task.started_at = datetime.now(timezone.utc)
        if task.status in ("success", "failed") and task.completed_at is None:
            task.completed_at = datetime.now(timezone.utc)
        self.session.add(task)
        await self.session.flush()
        return TaskResponse.model_validate(task)

    async def list_tasks(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Tuple[list[TaskResponse], int]:
        stmt = select(Task)
        if status:
            stmt = stmt.where(Task.status == status)
        if user_id is not None:
            stmt = stmt.where(Task.user_id == user_id)
        stmt = stmt.order_by(Task.created_at.desc())
        total_result = await self.session.execute(select(Task).select_from(stmt.subquery()))
        total = len(total_result.scalars().all())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(stmt)
        return [TaskResponse.model_validate(t) for t in result.scalars().all()], total

    async def delete_task(self, task_id: int) -> None:
        result = await self.session.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            raise NotFoundError("Task not found")
        await self.session.delete(task)