from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.apps.friends.schemas import FriendRequestCreate, FriendRequestStatus, FriendRequestOut
from src.apps.friends.models import FriendRequest
from src.apps.users.models import User
from src.apps.users.schemas import UserOut
from src.databases import get_async_db
from src.apps.users.routers import get_current_user


friend_router = APIRouter()


#send a friend request
@friend_router.post("/requests", response_model=FriendRequestOut, status_code=status.HTTP_201_CREATED)
async def send_friend_request(
    data: FriendRequestCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):
    if data.to_username == current_user.username:
        raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")


    user_query = select(User).where(User.username == data.to_username)
    to_user = (await session.execute(user_query)).scalars().first()

    if not to_user:
        raise HTTPException(status_code=404, detail="User not found")


    user_query = select(FriendRequest).where(
        or_(
            and_(FriendRequest.from_user_id == current_user.id, FriendRequest.to_user_id == to_user.id),
            and_(FriendRequest.from_user_id == to_user.id, FriendRequest.to_user_id == current_user.id),
        )
    )
    existing = (await session.execute(user_query)).scalars().first()
    if existing:
        if existing.status == FriendRequestStatus.pending:
            raise HTTPException(status_code=400, detail="Friend request already pending")
        elif existing.status == FriendRequestStatus.accepted:
            raise HTTPException(status_code=400, detail="You are already friends")


    friend_request = FriendRequest(
        from_user_id=current_user.id,
        to_user_id=to_user.id,
        status=FriendRequestStatus.pending,
    )
    session.add(friend_request)
    await session.commit()
    await session.refresh(friend_request)
    return friend_request


#accept request
@friend_router.post("/requests/{request_id}/accept", response_model=FriendRequestOut)
async def accept_friend_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):
    friend_request = await session.get(FriendRequest, request_id)
    if not friend_request or friend_request.to_user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Friend request not found")

    if friend_request.status != FriendRequestStatus.pending:
        raise HTTPException(status_code=400, detail="Friend request is not pending")

    friend_request.status = FriendRequestStatus.accepted
    await session.commit()
    await session.refresh(friend_request)
    return friend_request



#decline request
@friend_router.post("/requests/{request_id}/decline", response_model=FriendRequestOut)
async def reject_friend_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):
    friend_request = await session.get(FriendRequest, request_id)
    if not friend_request or friend_request.to_user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Friend request not found")

    if friend_request.status != FriendRequestStatus.pending:
        raise HTTPException(status_code=400, detail="Friend request is not pending")

    friend_request.status = FriendRequestStatus.declined
    await session.commit()
    await session.refresh(friend_request)
    return friend_request




#delete from friends
@friend_router.delete("/requests/{request_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_friend_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):
    friend_request = await session.get(FriendRequest, request_id)
    if not friend_request:
        raise HTTPException(status_code=404, detail="Friend request not found")

    if current_user.id not in [friend_request.from_user_id, friend_request.to_user_id]:
        raise HTTPException(status_code=403, detail="Not allowed to delete this friend request")

    await session.delete(friend_request)
    await session.commit()



#my friends list
@friend_router.get("/list", response_model=list[UserOut])
async def get_friends(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
):

    user_query = select(FriendRequest).where(or_(FriendRequest.from_user_id == current_user.id,FriendRequest.to_user_id == current_user.id),
    FriendRequest.status == FriendRequestStatus.accepted
    )

    results = await session.execute(user_query)
    friend_requests = results.scalars().all()

    friend_ids = []
    for fr in friend_requests:
        friend_id = fr.to_user_id if fr.from_user_id == current_user.id else fr.from_user_id
        friend_ids.append(friend_id)

    if not friend_ids:
        return []


    user_query = select(User).where(User.id.in_(friend_ids))
    friends_result = await session.execute(user_query)
    friends = friends_result.scalars().all()
    return friends
