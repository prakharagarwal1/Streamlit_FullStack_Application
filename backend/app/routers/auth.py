"""Auth router: register, login, refresh, profile."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPBearer

from app.schemas.user import TokenResponse, TokenRefresh, UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.database import get_db
from app.security import get_current_user_id, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=False)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db=Depends(get_db)):
    """Register a new user and return tokens."""
    service = UserService(db)
    return await service.register(payload)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserCreate, request: Request, db=Depends(get_db)):
    """Authenticate and return tokens."""
    service = UserService(db)
    return await service.login(payload.email, payload.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: TokenRefresh, db=Depends(get_db)):
    """Refresh access token using a valid refresh token."""
    service = UserService(db)
    return await service.refresh(payload.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(user=Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    payload: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    db=Depends(get_db),
):
    """Update the current user's profile."""
    service = UserService(db)
    return await service.update_profile(user_id, payload)