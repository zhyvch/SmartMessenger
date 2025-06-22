from datetime import datetime
from uuid import UUID

from beanie import Document


class ChatModel(Document):
    id: UUID
    created_at: datetime
    updated_at: datetime
    name: str
    is_group: bool
    owner_id: int
    member_ids: list[int]

    class Settings:
        name = "chats"
        indexes = [
            "id",
            "owner_id",
            "member_ids",
            [("created_at", -1)],
        ]


class MessageModel(Document):
    id: UUID
    created_at: datetime
    updated_at: datetime
    content: str
    is_read: bool
    read_by: list[int] = []
    sender_id: int
    chat_id: UUID

    class Settings:
        name = "messages"
        indexes = ["id", "chat_id", "sender_id", ("chat_id", "created_at")]


class ChatPermissionsModel(Document):
    id: UUID
    chat_id: UUID
    user_id: int
    can_send_messages: bool = True
    can_change_permissions: bool = False
    can_remove_members: bool = False
    can_delete_other_messages: bool = False

    class Settings:
        name = "chat_permissions"
        indexes = [
            "id",
            "chat_id",
            "user_id",
            ("chat_id", "user_id"),
        ]
