from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users.models import User
from src.databases import session_factory, get_async_db


def get_session():
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_async_db)
) -> User:
    user = await session.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")

    return user

CheckUserExistsByIDDep = Annotated[User, Depends(get_user_by_id)]
