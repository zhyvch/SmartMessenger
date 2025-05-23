from abc import ABC, abstractmethod
from uuid import UUID

from src.apps.chats.entities.chats import Chat, Message


class BaseChatRepository(ABC):
    @abstractmethod
    async def add_chat(self, chat: Chat) -> None:
        ...

    @abstractmethod
    async def get_chat(self, chat_id: UUID) -> Chat:
        ...

    @abstractmethod
    async def delete_chat(self, chat_id: UUID) -> None:
        ...


class BaseMessageRepository(ABC):
    @abstractmethod
    async def add_message(self, message: Message) -> None:
        ...

    @abstractmethod
    async def get_message(self, message_id: UUID) -> Message:
        ...

    @abstractmethod
    async def get_chat_messages(self, chat_id: UUID) -> list[Message]:
        ...

    @abstractmethod
    async def delete_message(self, message_id: UUID) -> None:
        ...
