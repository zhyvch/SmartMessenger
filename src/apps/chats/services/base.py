from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from src.apps.chats.schemas import UpdateChatPermissionsSchema
from src.apps.chats.entities import Chat, Message
from src.apps.chats.repositories import BaseChatRepository, BaseMessageRepository, BaseChatPermissionsRepository


@dataclass
class BaseChatService(ABC):
    chat_repo: BaseChatRepository
    message_repo: BaseMessageRepository
    chat_permissions_repo: BaseChatPermissionsRepository

    @abstractmethod
    async def create_private_chat(self, chat: Chat, other_user_id) -> None:
        ...

    @abstractmethod
    async def create_group_chat(self, chat: Chat) -> None:
        ...

    @abstractmethod
    async def get_chat(self, chat_id: UUID) -> Chat:
        ...

    @abstractmethod
    async def delete_chat(self, chat_id: UUID) -> None:
        ...

    @abstractmethod
    async def create_message(self, message: Message) -> None:
        ...

    @abstractmethod
    async def get_message(self, chat_id: UUID, message_id: UUID) -> Message:
        ...

    @abstractmethod
    async def get_messages(self, chat_id: UUID) -> list[Message]:
        ...

    @abstractmethod
    async def delete_message(self, chat_id: UUID, message_id: UUID) -> None:
        ...

    @abstractmethod
    async def add_chat_member(self, chat_id: UUID, user_id: int) -> None:
        ...

    @abstractmethod
    async def remove_chat_member(self, chat_id: UUID, user_id: int) -> None:
        ...

    @abstractmethod
    async def update_user_chat_permissions(
        self,
        chat_id: UUID,
        user_id: int,
        new_chat_permissions: UpdateChatPermissionsSchema
    ) -> None:
        ...
