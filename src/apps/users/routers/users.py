from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users.models import User
from src.apps.users.routers.auth import get_current_user
from src.apps.users.schemas import UserOut, UserUpdate
from src.databases import get_async_db

users_router = APIRouter()


# ─── Отримати список усіх активних користувачів ────────────────────────────────
@users_router.get("/", response_model=List[UserOut])
async def list_users(
    session: AsyncSession = Depends(get_async_db),
    current: User = Depends(get_current_user),
):
    """
    Повертає список усіх користувачів (тільки якщо поточний користувач авторизований).
    Можна додатково фільтрувати, пагінувати тощо.
    """
    q = select(User).where(User.is_active == True)
    result = await session.execute(q)
    users = result.scalars().all()
    return users


# ─── Отримати профіль поточного користувача ──────────────────────────────────────
@users_router.get("/me", response_model=UserOut)
async def read_own_profile(
    current: User = Depends(get_current_user),
):
    return current


# ─── Отримати профіль будь-якого користувача за ID ───────────────────────────────
@users_router.get("/{user_id}", response_model=UserOut)
async def read_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_async_db),
    current: User = Depends(get_current_user),
):
    user = await session.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


# ─── Оновити власний профіль ─────────────────────────────────────────────────────
@users_router.patch("/me", response_model=UserOut)
async def update_own_profile(
    data: UserUpdate,
    session: AsyncSession = Depends(get_async_db),
    current: User = Depends(get_current_user),
):
    """
    Відповідь: користувач може оновити своє first_name, last_name, phone_number тощо,
    за допомогою Pydantic-моделі UserUpdate.
    """
    # Приклад Pydantic-схеми (UserUpdate) має містити ті поля, які дозв. до зміни:
    # class UserUpdate(BaseModel):
    #     first_name: Optional[str]
    #     last_name: Optional[str]
    #     phone_number: Optional[str]
    #     username: Optional[str]
    #     ...
    #
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current, field, value)

    session.add(current)
    await session.commit()
    await session.refresh(current)
    return current


# ─── Видалити власний акаунт ─────────────────────────────────────────────────────
@users_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_own_account(
    session: AsyncSession = Depends(get_async_db),
    current: User = Depends(get_current_user),
):
    await session.delete(current)
    await session.commit()


# ─── Видалити користувача за ID (тільки адміністратор) ───────────────────────────
@users_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_async_db),
    current: User = Depends(get_current_user),
):
    # Припустимо, є поле current.is_superuser або current.is_admin, яке перевіряємо
    if not current.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    await session.delete(user)
    await session.commit()


# ─── Пошук користувача за email або username ─────────────────────────────────────
@users_router.get("/search/", response_model=List[UserOut])
async def search_users(
    email: Optional[str] = None,
    username: Optional[str] = None,
    session: AsyncSession = Depends(get_async_db),
    current: User = Depends(get_current_user),
):
    if not email and not username:
        raise HTTPException(
            status_code=400, detail="Provide email or username to search"
        )
    stmt = select(User)
    if email:
        stmt = stmt.where(User.email.ilike(f"%{email}%"))
    if username:
        stmt = stmt.where(User.username.ilike(f"%{username}%"))
    result = await session.execute(stmt)
    return result.scalars().all()
