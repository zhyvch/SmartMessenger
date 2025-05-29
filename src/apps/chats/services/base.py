from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from src.apps.chats.entities import Chat, Message
from src.apps.chats.repositories import BaseChatRepository, BaseMessageRepository


@dataclass
class BaseChatService(ABC):
    chat_repo: BaseChatRepository
    message_repo: BaseMessageRepository

    @abstractmethod
    async def create_chat(self, chat: Chat) -> None:
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
    async def get_message(self, message_id: UUID) -> Message:
        ...

    @abstractmethod
    async def get_messages(self, chat_id: UUID) -> list[Message]:
        ...

    @abstractmethod
    async def delete_message(self, message_id: UUID) -> None:
        ...
