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

    class Settings:
        name = 'chats'


class MessageModel(Document):
    id: UUID
    created_at: datetime
    updated_at: datetime
    content: str
    is_read: bool
    sender_id: int
    chat_id: UUID

    class Settings:
        name = 'messages'
