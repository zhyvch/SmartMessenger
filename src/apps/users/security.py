import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users.models import User
from src.settings.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def _create_token(
    subject: str | int,
    token_type: str,
    expires_delta: timedelta | None = None,
) -> str:
    now = datetime.now(tz=timezone.utc)
    expire = now + (
        expires_delta
        or timedelta(
            minutes=(
                settings.ACCESS_TOKEN_EXPIRE_MINUTES
                if token_type == "access"
                else settings.REFRESH_TOKEN_EXPIRE_MINUTES
            )
        )
    )
    jti = str(uuid.uuid4())
    payload = {
        "sub": str(subject),
        "type": token_type,
        "iat": now,
        "exp": expire,
        "jti": jti,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> str:
    return _create_token(subject, token_type="access", expires_delta=expires_delta)


def create_refresh_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> str:
    return _create_token(
        subject,
        token_type="refresh",
        expires_delta=expires_delta,
    )


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError as err:
        raise err


async def get_or_create_user(
    session: AsyncSession,
    *,
    google_id: str,
    email: str,
    name: Optional[str] = None,
) -> User:
    result = await session.execute(select(User).where(User.google_id == google_id))
    user = result.scalars().first()
    if user:
        return user

    result = await session.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if user:
        user.google_id = google_id
        await session.commit()
        await session.refresh(user)
        return user

    first_name = ""
    last_name = ""
    if name:
        parts = name.strip().split(" ", 1)
        first_name = parts[0]
        if len(parts) > 1:
            last_name = parts[1]

    new_user = User(
        email=email,
        google_id=google_id,
        first_name=first_name,
        last_name=last_name,
        is_active=True,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user
