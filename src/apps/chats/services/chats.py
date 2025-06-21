import logging
from dataclasses import dataclass
from uuid import UUID
from fastapi import HTTPException, status
import json

from apps.chats.schemas import UpdateChatPermissionsSchema
from src.apps.chats.entities import Chat, Message, ChatPermissions
from src.apps.chats.services import BaseChatService
from src.apps.chats.websocket.connections import ConnectionManager
from src.apps.ai.services import OpenAIService
from src.apps.ai.services import UnsplashService


logger = logging.getLogger(__name__)


@dataclass
class ChatService(BaseChatService):
    connection_manager: ConnectionManager
    ai_service: OpenAIService
    unsplash_service: UnsplashService

    async def create_private_chat(self, chat: Chat, other_user_id) -> None:
        logger.info('Creating private chat with id \'%s\'', chat.id)

        if chat.owner_id == other_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Users cannot create private chat with themselves"
            )

        existing_chat = await self.chat_repo.get_private_chat_by_member_ids(chat.owner_id, other_user_id)
        if existing_chat:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Users with ids {chat.owner_id} and {other_user_id} already have private chat with id "
                       f"{existing_chat.id}"
            )

        await self.chat_repo.add_chat(chat)

        created_chat = await self.get_chat(chat.id)
        created_chat.member_ids.append(other_user_id)
        await created_chat.save()

        await self.chat_permissions_repo.add_user_chat_permissions(ChatPermissions(
            chat_id=chat.id,
            user_id=chat.owner_id,
        ))
        await self.chat_permissions_repo.add_user_chat_permissions(ChatPermissions(
            chat_id=chat.id,
            user_id=other_user_id,
        ))

    async def create_group_chat(self, chat: Chat) -> None:
        logger.info('Creating group chat with id \'%s\'', chat.id)
        await self.chat_repo.add_chat(chat)
        await self.chat_permissions_repo.add_user_chat_permissions(ChatPermissions(
            chat_id=chat.id,
            user_id=chat.owner_id,
            can_send_messages=True,
            can_change_permissions=True,
            can_remove_members=True,
            can_delete_other_messages=True
        ))

    async def get_chat(self, chat_id: UUID) -> Chat:
        logger.info('Retrieving chat with id \'%s\'', chat_id)
        return await self.chat_repo.get_chat(chat_id)

    async def get_user_chats(self, user_id: int) -> list[Chat]:
        logger.info('Retrieving chats for user with id \'%s\'', user_id)
        return await self.chat_repo.get_user_chats(user_id)

    async def mark_message_as_read(self, chat_id: UUID, message_id: UUID, user_id: int) -> None:
        logger.info('Marking message with id \'%s\' as read by user with id \'%s\'', message_id, user_id)
        check_chat_exists = await self.get_chat(chat_id)

        message = await self.message_repo.get_message(message_id)
        if message.chat_id != chat_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Message with id {message_id} is not present in chat with id {chat_id}"
            )

        await self.message_repo.mark_message_as_read(message_id, user_id)

        # Notify other users that the message has been read
        await self.connection_manager.send_all(
            chat_id,
            json.dumps({
                "type": "message_read",
                "message_id": str(message_id),
                "user_id": user_id
            }).encode()
        )

    async def delete_chat(self, chat_id: UUID) -> None:
        logger.info('Deleting chat with id \'%s\'', chat_id)
        await self.chat_repo.delete_chat(chat_id)
        await self.message_repo.delete_chat_messages(chat_id)
        await self.chat_permissions_repo.delete_all_user_chat_permissions(chat_id)

    async def create_message(self, message: Message) -> None:
        logger.info('Creating message to chat with id \'%s\'', message.chat_id)
        check_chat_exists = await self.get_chat(message.chat_id)

        await self.message_repo.add_message(message)
        await self.connection_manager.send_all(message.chat_id, message.content.encode())

        if message.content.lower().startswith("@ai"):
            question = message.content[3:].strip()

            try:
                answer = await self.ai_service.ask(question)
            except HTTPException as e:
                answer = "Error while querying AI: " + e.detail

            ai_message = Message(
                chat_id=message.chat_id,
                sender_id="777",
                content=answer,
            )

            await self.message_repo.add_message(ai_message)
            await self.connection_manager.send_all(ai_message.chat_id, ai_message.content.encode())

        elif message.content.lower().startswith("@photo"):
            query = message.content[6:].strip()

            try:
                photo_url = await self.unsplash_service.search_photo(query)
            except HTTPException as e:
                photo_url = "Error while getting photo: " + e.detail

            photo_message = Message(
                chat_id=message.chat_id,
                sender_id="777",
                content=photo_url,
            )

            await self.message_repo.add_message(photo_message)
            await self.connection_manager.send_all(photo_message.chat_id, photo_message.content.encode())

    async def get_message(self, chat_id: UUID, message_id: UUID) -> Message:
        logger.info('Retrieving message with id \'%s\'', message_id)
        check_chat_exists = await self.get_chat(chat_id)

        message = await self.message_repo.get_message(message_id)
        if message.chat_id != chat_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Message with id {message_id} is not present in chat with id {chat_id}"
            )

        return message

    async def get_messages(self, chat_id: UUID) -> list[Message]:
        logger.info('Retrieving messages for chat with id \'%s\'', chat_id)
        return await self.message_repo.get_chat_messages(chat_id)

    async def delete_message(self, chat_id: UUID, message_id: UUID) -> None:
        logger.info('Deleting message with id \'%s\'', message_id)
        check_chat_exists = await self.get_chat(chat_id)

        message = await self.message_repo.get_message(message_id)
        if message.chat_id != chat_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Message with id {message_id} is not present in chat with id {chat_id}"
            )

        await self.message_repo.delete_message(message_id)

    async def add_chat_member(self, chat_id: UUID, user_id: int) -> None:
        logger.info('Adding chat member with id \'%s\' to chat with id \'%s\'', user_id, chat_id)
        chat = await self.get_chat(chat_id)

        if not chat.is_group:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No users can be added to private chat"
            )

        if user_id in chat.member_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with id {user_id} already is a member of chat with id {chat_id}"
            )

        chat.member_ids.append(user_id)
        await chat.save()

        await self.chat_permissions_repo.add_user_chat_permissions(ChatPermissions(
            chat_id=chat_id,
            user_id=user_id,
        ))

    async def remove_chat_member(self, chat_id: UUID, user_id: int) -> None:
        logger.info('Removing chat member with id \'%s\' from chat with id \'%s\'', user_id, chat_id)
        chat = await self.get_chat(chat_id)

        if not chat.is_group:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No users can be removed from private chat"
            )

        if user_id == chat.owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chat owner cannot be removed"
            )
        elif user_id not in chat.member_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with id {user_id} is not a member of chat with id {chat_id}"
            )

        chat.member_ids.remove(user_id)
        await chat.save()

        await self.chat_permissions_repo.delete_user_chat_permissions(chat_id=chat_id, user_id=user_id)

    async def update_user_chat_permissions(
        self,
        chat_id: UUID,
        user_id: int,
        new_chat_permissions: UpdateChatPermissionsSchema
    ) -> None:
        logger.info('Updating chat permissions for member with id \'%s\' in chat with id \'%s\'', user_id, chat_id)
        chat = await self.get_chat(chat_id)

        if not chat.is_group:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User`s chat permissions cannot be changed in private chat"
            )

        if user_id == chat.owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Owner`s chat permissions cannot be changed"
            )
        elif user_id not in chat.member_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with id {user_id} is not a member of chat with id {chat_id}"
            )

        await self.chat_permissions_repo.update_user_chat_permissions(
            chat_id=chat_id,
            user_id=user_id,
            new_chat_permissions=new_chat_permissions
        )
