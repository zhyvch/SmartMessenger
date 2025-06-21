import logging
from uuid import UUID
from beanie.operators import In

from src.apps.chats.schemas import UpdateChatPermissionsSchema
from src.apps.chats.exceptions import ChatNotFoundException, MessageNotFoundException, ChatPermissionsNotFoundException
from src.apps.chats.converters import ChatConverter, MessageConverter, ChatPermissionsConverter
from src.apps.chats.entities import Chat, Message, ChatPermissions
from src.apps.chats.models import ChatModel, MessageModel, ChatPermissionsModel
from src.apps.chats.repositories import BaseChatRepository, BaseMessageRepository, BaseChatPermissionsRepository


logger = logging.getLogger(__name__)


class BeanieChatRepository(BaseChatRepository):
    model = ChatModel
    converter = ChatConverter

    async def add_chat(self, chat: Chat) -> None:
        logger.info('Adding chat with id \'%s\'', chat.id)
        await self.model.insert_one(self.converter.to_model(chat))

    async def get_user_chats(self, user_id: int) -> list[Chat]:
        logger.info('Retrieving chats for user with id \'%s\'', user_id)
        chats = await self.model.find(
            In(self.model.member_ids, [user_id])
        ).to_list()
        return [self.converter.to_entity(chat) for chat in chats]

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

    async def get_private_chat_by_member_ids(self, member_1_id: int, member_2_id: int) -> Chat | None:
        logger.info('Getting private chat with member ids: \'%s\' and \'%s\'', member_1_id, member_2_id)
        chat = await self.model.find_one(
            self.model.is_group is False,
            In(self.model.member_ids, [member_1_id]),
            In(self.model.member_ids, [member_2_id])
        )

        return self.converter.to_entity(chat) if chat else None


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

    async def mark_message_as_read(self, message_id: UUID, user_id: int) -> None:
        logger.info('Marking message with id \'%s\' as read by user with id \'%s\'', message_id, user_id)
        message = await self.model.find_one(self.model.id == message_id)
        if message is None:
            logger.error('Message with id \'%s\' not found', message_id)
            raise MessageNotFoundException(message_id=message_id)

        if user_id not in message.read_by:
            message.read_by.append(user_id)
            message.is_read = True
            await message.save()

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

    async def delete_chat_messages(self, chat_id: UUID) -> None:
        logger.info('Deleting messages for chat with id \'%s\'', chat_id)
        await self.model.find(self.model.chat_id == chat_id).delete()


class BeanieChatPermissionsRepository(BaseChatPermissionsRepository):
    model = ChatPermissionsModel
    converter = ChatPermissionsConverter

    async def get_user_chat_permissions(self, chat_id: UUID, user_id: int) -> ChatPermissions:
        logger.info('Retrieving chat permissions for user with id \'%s\' in chat with id \'%s\'',
                    chat_id, user_id
                    )
        chat_permissions = await self.model.find_one(
            self.model.chat_id == chat_id,
            self.model.user_id == user_id
        )
        if chat_permissions is None:
            logger.error('Chat permissions for user with id \'%s\' in chat with id \'%s\' not found', user_id, chat_id)
            raise ChatPermissionsNotFoundException(chat_id=chat_id, user_id=user_id)

        return self.converter.to_entity(chat_permissions)

    async def add_user_chat_permissions(self, chat_permissions: ChatPermissions) -> None:
        logger.info('Adding chat permissions with id \'%s\'', chat_permissions.id)
        await self.model.insert_one(self.converter.to_model(chat_permissions))

    async def delete_all_user_chat_permissions(self, chat_id: UUID) -> None:
        logger.info('Deleting all chat permissions for chat with id \'%s\'', chat_id)
        await self.model.find(self.model.chat_id == chat_id).delete()

    async def delete_user_chat_permissions(self, chat_id: UUID, user_id: int) -> None:
        logger.info('Deleting chat permissions for member with id \'%s\' in chat with id \'%s\'', user_id, chat_id)
        chat_permissions = await self.model.find_one(
            self.model.chat_id == chat_id,
            self.model.user_id == user_id
        )
        if chat_permissions is None:
            logger.error('Chat permissions for user with id \'%s\' in chat with id \'%s\' not found', user_id, chat_id)
            raise ChatPermissionsNotFoundException(chat_id=chat_id, user_id=user_id)

        await chat_permissions.delete()

    async def update_user_chat_permissions(
        self,
        chat_id: UUID,
        user_id: int,
        new_chat_permissions: UpdateChatPermissionsSchema
    ) -> None:
        logger.info('Updating chat permissions for member with id \'%s\' in chat with id \'%s\'', user_id, chat_id)
        chat_permissions = await self.model.find_one(
            self.model.chat_id == chat_id,
            self.model.user_id == user_id
        )
        if chat_permissions is None:
            logger.error('Chat permissions for user with id \'%s\' in chat with id \'%s\' not found', user_id, chat_id)
            raise ChatPermissionsNotFoundException(chat_id=chat_id, user_id=user_id)

        await chat_permissions.set({
            self.model.can_send_messages: new_chat_permissions.can_send_messages,
            self.model.can_change_permissions: new_chat_permissions.can_change_permissions,
            self.model.can_remove_members: new_chat_permissions.can_remove_members,
            self.model.can_delete_other_messages: new_chat_permissions.can_delete_other_messages
        })
