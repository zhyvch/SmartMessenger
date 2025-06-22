from src.apps.chats.entities import Chat as ChatEntity
from src.apps.chats.entities import ChatPermissions as ChatPermissionsEntity
from src.apps.chats.entities import Message as MessageEntity
from src.apps.chats.exceptions import (
    IsNotChatEntityException,
    IsNotChatModelException,
    IsNotChatPermissionsEntityException,
    IsNotChatPermissionsModelException,
    IsNotMessageEntityException,
    IsNotMessageModelException,
)
from src.apps.chats.models import ChatModel, ChatPermissionsModel, MessageModel


class ChatConverter:
    @classmethod
    def to_model(cls, chat: ChatEntity) -> ChatModel:
        if not isinstance(chat, ChatEntity):
            raise IsNotChatEntityException(gotten_type=type(chat).__name__)

        return ChatModel(
            id=chat.id,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            name=chat.name,
            is_group=chat.is_group,
            owner_id=chat.owner_id,
            member_ids=[item for item in chat.member_ids],
        )

    @classmethod
    def to_entity(cls, chat: ChatModel) -> ChatEntity:
        if not isinstance(chat, ChatModel):
            raise IsNotChatModelException(gotten_type=type(chat).__name__)

        return ChatEntity(
            id=chat.id,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            name=chat.name,
            is_group=chat.is_group,
            owner_id=chat.owner_id,
            member_ids=[item for item in chat.member_ids],
        )


class MessageConverter:
    @classmethod
    def to_model(cls, message: MessageEntity) -> MessageModel:
        if not isinstance(message, MessageEntity):
            raise IsNotMessageEntityException(gotten_type=type(message).__name__)

        return MessageModel(
            id=message.id,
            created_at=message.created_at,
            updated_at=message.updated_at,
            content=message.content,
            is_read=message.is_read,
            read_by=message.read_by,
            sender_id=message.sender_id,
            chat_id=message.chat_id,
        )

    @classmethod
    def to_entity(cls, message: MessageModel) -> MessageEntity:
        if not isinstance(message, MessageModel):
            raise IsNotMessageModelException(gotten_type=type(message).__name__)

        return MessageEntity(
            id=message.id,
            created_at=message.created_at,
            updated_at=message.updated_at,
            content=message.content,
            read_by=message.read_by,
            is_read=message.is_read,
            sender_id=message.sender_id,
            chat_id=message.chat_id,
        )


class ChatPermissionsConverter:
    @classmethod
    def to_model(cls, chat_permissions: ChatPermissionsEntity) -> ChatPermissionsModel:
        if not isinstance(chat_permissions, ChatPermissionsEntity):
            raise IsNotChatPermissionsEntityException(
                gotten_type=type(chat_permissions).__name__
            )

        return ChatPermissionsModel(
            id=chat_permissions.id,
            chat_id=chat_permissions.chat_id,
            user_id=chat_permissions.user_id,
            can_send_messages=chat_permissions.can_send_messages,
            can_change_permissions=chat_permissions.can_change_permissions,
            can_remove_members=chat_permissions.can_remove_members,
            can_delete_other_messages=chat_permissions.can_delete_other_messages,
        )

    @classmethod
    def to_entity(cls, chat_permissions: ChatPermissionsModel) -> ChatPermissionsEntity:
        if not isinstance(chat_permissions, ChatPermissionsModel):
            raise IsNotChatPermissionsModelException(
                gotten_type=type(chat_permissions).__name__
            )

        return ChatPermissionsEntity(
            id=chat_permissions.id,
            chat_id=chat_permissions.chat_id,
            user_id=chat_permissions.user_id,
            can_send_messages=chat_permissions.can_send_messages,
            can_change_permissions=chat_permissions.can_change_permissions,
            can_remove_members=chat_permissions.can_remove_members,
            can_delete_other_messages=chat_permissions.can_delete_other_messages,
        )
