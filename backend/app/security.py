"""Security helpers: password hashing, JWT tokens, rate limiting keys."""
from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional, Tuple

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select

from app.config import get_settings
from app.database import get_db as _get_db
from app.models.user import User

settings = get_settings()

# --- Rate limiting ----------------------------------------------------------
try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
except Exception:  # pragma: no cover - optional dependency
    limiter = None  # type: ignore[assignment]

# --- Password hashing (bcrypt via passlib) ----------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return pwd_context.verify(plain, hashed)
    except ValueError:
        return False


# --- JWT --------------------------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = dict(data)
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update(
        {
            "exp": expire,
            "iat": now,
            "jti": uuid.uuid4().hex,  # unique token id for revocation
        }
    )
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a long-lived refresh token."""
    return create_access_token(
        data,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT. Returns the payload or None on failure."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


# --- Token helpers ----------------------------------------------------------
def make_token_pair(user_id: int, username: str, role: str) -> dict:
    """Return access + refresh tokens for a user."""
    payload = {"sub": str(user_id), "username": username, "role": role}
    return {
        "access_token": create_access_token(payload),
        "refresh_token": create_refresh_token(payload),
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


# --- API key (for service-to-service / MCP-style access) --------------------
def generate_api_key() -> str:
    """Generate a random API key."""
    return f"sk_{secrets.token_urlsafe(32)}"


def hash_api_key(key: str) -> str:
    """Store a one-way SHA-256 of an API key."""
    return hashlib.sha256(key.encode()).hexdigest()


def constant_time_compare(a: str, b: str) -> bool:
    """Constant-time string comparison to avoid timing attacks."""
    return hmac.compare_digest(a, b)


def generate_token_pair(user_id: int, role: str) -> dict:
    """Return access + refresh tokens for a user."""
    return {
        "access_token": create_access_token({"sub": str(user_id), "role": role}),
        "refresh_token": create_refresh_token({"sub": str(user_id), "role": role}),
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


def generate_api_key() -> str:
    """Generate a random API key string."""
    return "sk-" + uuid.uuid4().hex + uuid.uuid4().hex[:8]


def generate_otp(length: int = 6) -> str:
    """Generate a numeric one-time password."""
    return "".join(secrets.choice("0123456789") for _ in range(length))


def generate_slug(*parts: str) -> str:
    """Generate a URL-safe slug from parts."""
    from slugify import slugify

    return slugify("-".join(str(p) for p in parts if p))


# --- FastAPI dependencies ---------------------------------------------------
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.user import User
from app.database import get_db as _get_db

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
) -> User:
    """Return the authenticated User object from a Bearer token."""
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_NOT_AUTHENTICATED, detail="Not authenticated")
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_NOT_AUTHENTICATED, detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_NOT_AUTHENTICATED, detail="Invalid token payload")
    async with _get_db().__aiter__() as session:
        result = await session.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_NOT_AUTHENTICATED, detail="User not found")
        return user


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
) -> int:
    """Return the authenticated user's ID."""
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_NOT_AUTHENTICATED, detail="Not authenticated")
    payload = decode_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_NOT_AUTHENTICATED, detail="Invalid token")
    return int(payload["sub"])


async def require_admin(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
) -> User:
    """Dependency that requires an admin role."""
    user = await get_current_user(credentials)
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


# Late import to avoid circular dependency
from sqlalchemy import select  # noqa: E402