import os
from datetime import datetime, timedelta
from typing import Optional, Union
import uuid
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.settings.config import settings

# Configuration
SECRET_KEY = getattr(settings, "JWT_SECRET", os.getenv("JWT_SECRET", "changeme"))
ALGORITHM = getattr(settings, "JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 60)
REFRESH_TOKEN_EXPIRE_MINUTES = getattr(settings, "REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def _create_token(
    subject: Union[str, int],
    token_type: str,
    expires_delta: Optional[timedelta]
) -> str:
    now = datetime.utcnow()
    expire = now + (expires_delta or timedelta(
        minutes=(ACCESS_TOKEN_EXPIRE_MINUTES if token_type == "access" else REFRESH_TOKEN_EXPIRE_MINUTES)
    ))
    jti = str(uuid.uuid4())
    payload = {
        "sub": str(subject),
        "type": token_type,
        "iat": now,
        "exp": expire,
        "jti": jti,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None
) -> str:
    return _create_token(subject, token_type="access", expires_delta=expires_delta)


def create_refresh_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None
) -> str:
    return _create_token(
        subject,
        token_type="refresh",
        expires_delta=expires_delta or timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
    )


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as err:
        raise err