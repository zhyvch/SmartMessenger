from uuid import UUID, uuid4
from datetime import datetime, timezone

from pydantic import BaseModel
from pydantic.fields import Field


class Chat(BaseModel):
    id: UUID = Field(default_factory=uuid4, kw_only=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), kw_only=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), kw_only=True)
    name: str = Field(kw_only=True, max_length=255)
    is_group: bool = Field(default=False, kw_only=True)
    owner_id: int = Field(kw_only=True)
    member_ids: list[int] = Field(default_factory=list, kw_only=True)


class Message(BaseModel):
    id: UUID = Field(default_factory=uuid4, kw_only=True, exclude=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), kw_only=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), kw_only=True)
    content: str = Field(kw_only=True, max_length=255 * 1024)
    is_read: bool = Field(default=False, kw_only=True)
    read_by: list[int] = Field(default_factory=list, kw_only=True)
    sender_id: int = Field(kw_only=True)
    chat_id: UUID = Field(kw_only=True)


class ChatWithMessages(BaseModel):
    chat: Chat
    messages: list[Message] = Field(default_factory=list, kw_only=True)


class ChatPermissions(BaseModel):
    id: UUID = Field(default_factory=uuid4, kw_only=True)
    chat_id: UUID = Field(kw_only=True)
    user_id: int = Field(kw_only=True)
    can_send_messages: bool = Field(default=True, kw_only=True)
    can_change_permissions: bool = Field(default=False, kw_only=True)
    can_remove_members: bool = Field(default=False, kw_only=True)
    can_delete_other_messages: bool = Field(default=False, kw_only=True)
