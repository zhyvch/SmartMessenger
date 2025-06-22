from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from src.apps.chats.entities import Chat, Message


class Order(Enum):
    ASC = 'asc'
    DESC = 'desc'


class Pagination(BaseModel):
    limit: int = 10
    offset: int = 0
    ordering: Order = Order.ASC


class CreateChatSchema(BaseModel):
    name: str = Field(min_length=1, max_length=255)

    def to_entity(self, owner_id: int, is_group: bool) -> Chat:
        return Chat(
            name=self.name, is_group=is_group, owner_id=owner_id, member_ids=[owner_id]
        )


class CreateMessageSchema(BaseModel):
    content: str = Field(min_length=1, max_length=255 * 1024)

    def to_entity(self, chat_id: UUID, sender_id: int) -> Message:
        return Message(
            content=self.content,
            sender_id=sender_id,
            chat_id=chat_id,
        )


class UpdateChatPermissionsSchema(BaseModel):
    can_send_messages: bool = Field(default=True)
    can_change_permissions: bool = Field(default=False)
    can_remove_members: bool = Field(default=False)
    can_delete_other_messages: bool = Field(default=False)
