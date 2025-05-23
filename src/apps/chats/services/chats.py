import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from src.api.v1.websocket.connections import ConnectionManager
from src.apps.chats.entities.chats import Chat, Message
from src.apps.chats.repositories.base import BaseChatRepository, BaseMessageRepository
from src.apps.chats.repositories.mongodb import MongoDBChatRepository


logger = logging.getLogger(__name__)


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


@dataclass
class ChatService(BaseChatService):
    connection_manager: ConnectionManager

    async def create_chat(self, chat: Chat) -> None:
        logger.info('Creating chat with id \'%s\'', chat.id)
        await self.chat_repo.add_chat(chat)

    async def get_chat(self, chat_id: UUID) -> Chat:
        logger.info('Retrieving chat with id \'%s\'', chat_id)
        return await self.chat_repo.get_chat(chat_id)

    async def delete_chat(self, chat_id: UUID) -> None:
        logger.info('Deleting chat with id \'%s\'', chat_id)
        await self.chat_repo.delete_chat(chat_id)

    async def create_message(self, message: Message) -> None:
        logger.info('Creating message to chat with id \'%s\'', message.chat_id)
        await self.message_repo.add_message(message)
        await self.connection_manager.send_all(message.chat_id, message.content.encode())

    async def get_message(self, message_id: UUID) -> Message:
        logger.info('Retrieving message with id \'%s\'', message_id)
        return await self.message_repo.get_message(message_id)

    async def get_messages(self, chat_id: UUID) -> list[Message]:
        logger.info('Retrieving messages for chat with id \'%s\'', chat_id)
        return await self.message_repo.get_chat_messages(chat_id)

    async def delete_message(self, message_id: UUID) -> None:
        logger.info('Deleting message with id \'%s\'', message_id)
        await self.message_repo.delete_message(message_id)
