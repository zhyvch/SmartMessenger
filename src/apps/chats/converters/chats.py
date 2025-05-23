from src.apps.chats.entities.chats import Chat as ChatEntity, Message as MessageEntity
from src.apps.chats.models.chats import ChatModel, MessageModel


class ChatConverter:
    @classmethod
    def to_model(cls, chat: ChatEntity) -> ChatModel:
        if not isinstance(chat, ChatEntity):
            raise Exception(f'Wrong type. Expected ChatEntity, got {type(chat)=}')

        return ChatModel(
            id=chat.id,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            name=chat.name,
            is_group=chat.is_group,
            owner_id=chat.owner_id,
        )

    @classmethod
    def to_entity(cls,chat: ChatModel) -> ChatEntity:
        if not isinstance(chat, ChatModel):
            raise Exception(f'Wrong type. Expected ChatModel, got {type(chat)=}')

        return ChatEntity(
            id=chat.id,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            name=chat.name,
            is_group=chat.is_group,
            owner_id=chat.owner_id,
        )


class MessageConverter:
    @classmethod
    def to_model(cls, message: MessageEntity) -> MessageModel:
        if not isinstance(message, MessageEntity):
            raise Exception(f'Wrong type. Expected MessageEntity, got {type(message)=}')

        return MessageModel(
            id=message.id,
            created_at=message.created_at,
            updated_at=message.updated_at,
            content=message.content,
            is_read=message.is_read,
            sender_id=message.sender_id,
            chat_id=message.chat_id,
        )

    @classmethod
    def to_entity(cls, message: MessageModel) -> MessageEntity:
        if not isinstance(message, MessageModel):
            raise Exception(f'Wrong type. Expected MessageModel, got {type(message)=}')

        return MessageEntity(
            id=message.id,
            created_at=message.created_at,
            updated_at=message.updated_at,
            content=message.content,
            is_read=message.is_read,
            sender_id=message.sender_id,
            chat_id=message.chat_id,
        )
