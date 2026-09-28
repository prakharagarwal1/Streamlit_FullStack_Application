"""User service: registration, auth, profile management."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import UserRole
from app.exceptions import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserResponse, UserUpdate
from app.security import (
    generate_token_pair,
    hash_password,
    verify_password,
)


class UserService:
    """Encapsulates user-related business logic."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def register(self, payload: UserCreate) -> TokenResponse:
        """Register a new user and return tokens + profile."""
        # Check for existing email / username
        existing = await self.session.execute(
            select(User).where(
                (User.email == payload.email) | (User.username == payload.username)
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError("Username or email already registered")

        user = User(
            username=payload.username,
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
            role=UserRole.USER.value,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        tokens = generate_token_pair(user.id, user.role)
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=self._to_response(user),
        )

    async def login(self, email: str, password: str) -> TokenResponse:
        """Authenticate a user and return tokens."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise ForbiddenError("Account is deactivated")
        user.last_login_at = datetime.now(timezone.utc)
        self.session.add(user)
        await self.session.flush()
        tokens = generate_token_pair(user.id, user.role)
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=self._to_response(user),
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        """Issue a new access token from a valid refresh token."""
        from app.security import decode_token

        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid or expired refresh token")
        user_id = int(payload["sub"])
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive")
        tokens = generate_token_pair(user.id, user.role)
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=self._to_response(user),
        )

    async def get_by_id(self, user_id: int) -> UserResponse:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User not found")
        return self._to_response(user)

    async def update_profile(
        self, user_id: int, payload: UserUpdate
    ) -> UserResponse:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User not found")
        if payload.full_name is not None:
            user.full_name = payload.full_name
        if payload.bio is not None:
            user.bio = payload.bio
        if payload.avatar_url is not None:
            user.avatar_url = payload.avatar_url
        self.session.add(user)
        await self.session.flush()
        return self._to_response(user)

    async def list_users(
        self, page: int = 1, page_size: int = 20, role: Optional[str] = None
    ) -> Tuple[list[UserResponse], int]:
        stmt = select(User)
        if role:
            stmt = stmt.where(User.role == role)
        stmt = stmt.order_by(User.created_at.desc())
        total_result = await self.session.execute(select(User).join(User.__table__, from_obj=User.__table__).select())
        total = len((await self.session.execute(select(User))).scalars().all())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return [self._to_response(u) for u in users], total

    @staticmethod
    def _to_response(user: User) -> UserResponse:
        return UserResponse.model_validate(user)