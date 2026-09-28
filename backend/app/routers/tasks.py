"""Tasks router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.database import get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.schemas.common import PageResponse
from app.services.task_service import TaskService
from app.security import get_current_user_id

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    user_id: int | None = Depends(get_current_user_id),
    db=Depends(get_db),
):
    service = TaskService(db)
    return await service.create_task(payload, user_id=user_id)


@router.get("", response_model=PageResponse[TaskResponse])
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    user_id: int | None = Query(None),
    db=Depends(get_db),
):
    service = TaskService(db)
    items, total = await service.list_tasks(
        page=page, page_size=page_size, status=status, user_id=user_id
    )
    pages = max(1, (total + page_size - 1) // page_size)
    return PageResponse[TaskResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db=Depends(get_db)):
    service = TaskService(db)
    return await service.get_task(task_id)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, payload: TaskUpdate, db=Depends(get_db)):
    service = TaskService(db)
    return await service.update_task(task_id, payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db=Depends(get_db)):
    service = TaskService(db)
    await service.delete_task(task_id)