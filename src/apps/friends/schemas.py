from pydantic import BaseModel
from enum import Enum


class FriendRequestStatusEnum(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class FriendRequestCreate(BaseModel):
    receiver_id: int


class FriendRequestResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    status: FriendRequestStatusEnum

    class Config:
        orm_mode = True
