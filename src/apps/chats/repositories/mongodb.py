import logging
from uuid import UUID

from src.apps.chats.exceptions import ChatNotFoundException, MessageNotFoundException
from src.apps.chats.converters import ChatConverter, MessageConverter
from src.apps.chats.entities import Chat, Message
from src.apps.chats.models import ChatModel, MessageModel
from src.apps.chats.repositories import BaseChatRepository, BaseMessageRepository


logger = logging.getLogger(__name__)


class BeanieChatRepository(BaseChatRepository):
    model = ChatModel
    converter = ChatConverter

    async def add_chat(self, chat: Chat) -> None:
        logger.info('Adding chat with id \'%s\'', chat.id)
        await self.model.insert_one(self.converter.to_model(chat))

    async def get_chat(self, chat_id: UUID) -> Chat:
        logger.info('Retrieving chat with id \'%s\'', chat_id)
        chat = await self.model.find_one(self.model.id == chat_id)
        if chat is None:
            logger.error('Chat with id \'%s\' not found', chat_id)
            raise ChatNotFoundException(chat_id=chat_id)

        return self.converter.to_entity(chat)

    async def delete_chat(self, chat_id: UUID) -> None:
        logger.info('Deleting chat with id \'%s\'', chat_id)
        chat = await self.model.find_one(self.model.id == chat_id)
        if chat is None:
            logger.error('Chat with id \'%s\' not found', chat_id)
            raise ChatNotFoundException(chat_id=chat_id)

        await chat.delete()


class BeanieMessageRepository(BaseMessageRepository):
    model = MessageModel
    converter = MessageConverter

    async def add_message(self, message: Message) -> None:
        logger.info('Adding message with id \'%s\'', message.id)
        await self.model.insert_one(self.converter.to_model(message))

    async def get_message(self, message_id: UUID) -> Message:
        logger.info('Retrieving message with id \'%s\'', message_id)
        message = await self.model.find_one(self.model.id == message_id)
        if message is None:
            logger.error('Message with id \'%s\' not found', message_id)
            raise MessageNotFoundException(message_id=message_id)

        return self.converter.to_entity(message)

    async def get_chat_messages(self, chat_id: UUID) -> list[Message]:
        logger.info('Retrieving messages for chat with id \'%s\'', chat_id)
        chat = await ChatModel.find_one(ChatModel.id == chat_id)
        if chat is None:
            logger.error('Chat with id \'%s\' not found', chat_id)
            raise ChatNotFoundException(chat_id=chat_id)

        messages = await self.model.find(self.model.chat_id == chat_id).to_list()
        return [self.converter.to_entity(message) for message in messages]

    async def delete_message(self, message_id: UUID) -> None:
        logger.info('Deleting message with id \'%s\'', message_id)
        message = await self.model.find_one(self.model.id == message_id)
        if message is None:
            logger.error('Message with id \'%s\' not found', message_id)
            raise MessageNotFoundException(message_id=message_id)

        await message.delete()
