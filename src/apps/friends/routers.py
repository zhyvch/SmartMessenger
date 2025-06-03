from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

#from src.databases import get_db
from src.apps.users.schemas import UserOut
from src.apps.users.routers import get_current_user
from src.apps.users.models import User
from apps.friends.models import FriendRequest, Friend, RequestStatus
from apps.friends.schemas import FriendRequestCreate, FriendRequestResponse

router = APIRouter(prefix="/friends_router", tags=["Friends"])


@router.post("/request", response_model=FriendRequestResponse)
async def send_friend_request(
    request: FriendRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id == request.receiver_id:
        raise HTTPException(status_code=400, detail="Неможливо надіслати запит самому собі")

    stmt = select(FriendRequest).where(
        or_(
            (FriendRequest.sender_id == current_user.id) & (FriendRequest.receiver_id == request.receiver_id),
            (FriendRequest.sender_id == request.receiver_id) & (FriendRequest.receiver_id == current_user.id)
        )
    )
    result = await db.execute(stmt)
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Запит уже існує або очікує відповіді")

    friend_request = FriendRequest(
        sender_id=current_user.id,
        receiver_id=request.receiver_id,
        status=RequestStatus.pending
    )
    db.add(friend_request)
    await db.commit()
    await db.refresh(friend_request)

    return friend_request


@router.post("/accept/{request_id}", response_model=dict)
async def accept_friend_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(FriendRequest).where(FriendRequest.id == request_id)
    result = await db.execute(stmt)
    friend_request = result.scalars().first()

    if not friend_request:
        raise HTTPException(status_code=404, detail="Запит не знайдено")
    if friend_request.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Це не ваш запит")
    if friend_request.status != RequestStatus.pending:
        raise HTTPException(status_code=400, detail="Запит вже оброблено")

    # Оновлюємо статус
    friend_request.status = RequestStatus.accepted

    # Додаємо обох у friends
    db.add_all([
        Friend(user_id=friend_request.sender_id, friend_id=friend_request.receiver_id),
        Friend(user_id=friend_request.receiver_id, friend_id=friend_request.sender_id),
    ])

    await db.commit()

    return {"detail": "Запит прийнято та збережено в друзях"}


@router.delete("/reject/{request_id}", response_model=dict)
async def reject_friend_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(FriendRequest).where(FriendRequest.id == request_id)
    result = await db.execute(stmt)
    friend_request = result.scalars().first()

    if not friend_request:
        raise HTTPException(status_code=404, detail="Запит не знайдено")
    if current_user.id not in [friend_request.sender_id, friend_request.receiver_id]:
        raise HTTPException(status_code=403, detail="Ви не маєте прав на цю дію")

    await db.delete(friend_request)
    await db.commit()

    return {"detail": "Запит видалено"}


@router.get("/incoming", response_model=List[FriendRequestResponse])
async def get_incoming_friend_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(FriendRequest).where(
        FriendRequest.receiver_id == current_user.id,
        FriendRequest.status == RequestStatus.pending
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/outgoing", response_model=List[FriendRequestResponse])
async def get_outgoing_friend_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(FriendRequest).where(
        FriendRequest.sender_id == current_user.id,
        FriendRequest.status == RequestStatus.pending
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/list", response_model=List[UserOut])
async def get_all_friends(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Friend.friend_id).where(Friend.user_id == current_user.id)
    result = await db.execute(stmt)
    friend_ids = [row[0] for row in result.all()]

    if not friend_ids:
        return []

    stmt = select(User).where(User.id.in_(friend_ids))
    result = await db.execute(stmt)
    return result.scalars().all()
