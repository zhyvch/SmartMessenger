from pydantic import BaseModel
from src.apps.friends.models import FriendRequestStatus

class FriendRequestCreate(BaseModel):
    to_username: str

class FriendRequestOut(BaseModel):
    id: int
    from_user_id: int
    to_user_id: int
    status: FriendRequestStatus

    model_config = {
        "from_attributes": True
    }
