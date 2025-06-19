from enum import Enum
from uuid import UUID

from pydantic import BaseModel

from src.apps.chats.entities import Chat, Message


class Order(Enum):
    ASC = "asc"
    DESC = "desc"


class Pagination(BaseModel):
    limit: int = 10
    offset: int = 0
    ordering: Order = Order.ASC


class CreateChatSchema(BaseModel):
    name: str

    def to_entity(self, owner_id: int, is_group: bool) -> Chat:
        return Chat(
            name=self.name, is_group=is_group, owner_id=owner_id, member_ids=[owner_id]
        )


class CreateMessageSchema(BaseModel):
    content: str

    def to_entity(self, chat_id: UUID, sender_id: int) -> Message:
        return Message(
            content=self.content,
            sender_id=sender_id,
            chat_id=chat_id,
        )


class UpdateChatPermissionsSchema(BaseModel):
    can_send_messages: bool = True
    can_change_permissions: bool = False
    can_remove_members: bool = False
    can_delete_other_messages: bool = False
