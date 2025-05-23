import logging
from uuid import UUID

from src.apps.chats.converters.chats import ChatConverter, MessageConverter
from src.apps.chats.entities.chats import Chat, Message
from src.apps.chats.models.chats import ChatModel, MessageModel
from src.apps.chats.repositories.base import BaseChatRepository, BaseMessageRepository


logger = logging.getLogger(__name__)


class MongoDBChatRepository(BaseChatRepository):
    model = ChatModel
    converter = ChatConverter

    async def add_chat(self, chat: Chat) -> None:
        logger.info('Adding chat with id \'%s\'', chat.id)
        await self.model.insert_one(self.converter.to_model(chat))

    async def get_chat(self, chat_id: UUID) -> Chat:
        logger.info('Retrieving chat with id \'%s\'', chat_id)
        return self.converter.to_entity(await self.model.find_one(self.model.id == chat_id))

    async def delete_chat(self, chat_id: UUID) -> None:
        logger.info('Deleting chat with id \'%s\'', chat_id)
        await self.model.find_one(self.model.id == chat_id).delete()


class MongoDBMessageRepository(BaseMessageRepository):
    model = MessageModel
    converter = MessageConverter

    async def add_message(self, message: Message) -> None:
        logger.info('Adding message with id \'%s\'', message.id)
        await self.model.insert_one(self.converter.to_model(message))

    async def get_message(self, message_id: UUID) -> Message:
        logger.info('Retrieving message with id \'%s\'', message_id)
        return self.converter.to_entity(await self.model.find_one(self.model.id == message_id))

    async def get_chat_messages(self, chat_id: UUID) -> list[Message]:
        logger.info('Retrieving messages for chat with id \'%s\'', chat_id)
        messages = await self.model.find(self.model.chat_id == chat_id).to_list()
        return [self.converter.to_entity(message) for message in messages]

    async def delete_message(self, message_id: UUID) -> None:
        logger.info('Deleting message with id \'%s\'', message_id)
        await self.model.find_one(self.model.id == message_id).delete()
