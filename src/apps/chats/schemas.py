from uuid import UUID

from pydantic import BaseModel

from src.apps.chats.entities import Chat, Message


class CreateChatSchema(BaseModel):
    name: str
    is_group: bool = False
    owner_id: int

    def to_entity(self) -> Chat:
        return Chat(
            name=self.name,
            is_group=self.is_group,
            owner_id=self.owner_id,
        )


class CreateMessageSchema(BaseModel):
    content: str
    sender_id: int
    chat_id: UUID

    def to_entity(self) -> Message:
        return Message(
            content=self.content,
            sender_id=self.sender_id,
            chat_id=self.chat_id,
        )
