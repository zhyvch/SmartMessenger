from typing import Annotated

from fastapi import Depends, HTTPException, WebSocket, WebSocketException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users.models import User
from src.apps.users.security import decode_token
from src.databases import get_async_db, session_factory


def get_session():
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_user_by_id(
    user_id: int, session: AsyncSession = Depends(get_async_db)
) -> User:
    user = await session.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    return user


CheckUserExistsByIDDep = Annotated[User, Depends(get_user_by_id)]


async def get_current_websocket_user(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_async_db),
) -> User:
    token = websocket.query_params.get("token")

    if not token:
        auth_header = websocket.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[len("Bearer ") :]

    if not token:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason="No token provided"
        )

    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise ValueError()
        user_id = int(payload["sub"])
    except Exception:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token"
        )

    user = await session.get(User, user_id)
    if not user or not user.is_active:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason="Inactive user"
        )

    return user


CurrentWebsocketUserDep = Annotated[User, Depends(get_current_websocket_user)]
