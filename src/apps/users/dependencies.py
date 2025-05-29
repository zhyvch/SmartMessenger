from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.databases import session_factory


def get_session():
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


SessionDep = Annotated[AsyncSession, Depends(get_session)]
