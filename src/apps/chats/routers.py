import logging
from uuid import UUID

from fastapi import APIRouter, status

from src.apps.chats.dependencies import ChatServiceDep
from src.apps.chats.entities import Chat, Message, ChatWithMessages
from src.apps.chats.schemas import CreateChatSchema, CreateMessageSchema


logger = logging.getLogger(__name__)
chats_router = APIRouter()
messages_router = APIRouter()


@chats_router.post(
    '/',
    description='Creates a new chat.',
    status_code=status.HTTP_201_CREATED,
)
async def create_chat(
    schema: CreateChatSchema,
    service: ChatServiceDep,
) -> str:
    entity = schema.to_entity()
    await service.create_chat(entity)
    return f'Chat with id {entity.id} successfully created'


@chats_router.get(
    '/{chat_id}',
    description='Retrieves a chat by its ID.',
    status_code=status.HTTP_200_OK,
)
async def get_chat(
    chat_id: UUID,
    service: ChatServiceDep,
) -> Chat:
    return await service.get_chat(chat_id)


@chats_router.delete(
    '/{chat_id}',
    description='Deletes a chat by its ID.',
    status_code=status.HTTP_200_OK,
)
async def delete_chat(
    chat_id: UUID,
    service: ChatServiceDep,
) -> str:
    await service.delete_chat(chat_id)
    return f'Chat with id {chat_id} successfully deleted'


@chats_router.get(
    '/{chat_id}/messages',
    description='Retrieves all messages for a chat.',
    status_code=status.HTTP_200_OK,
)
async def get_chat_messages(
    chat_id: UUID,
    service: ChatServiceDep,
) -> ChatWithMessages:
    return ChatWithMessages(
        chat=await service.get_chat(chat_id),
        messages=await service.get_messages(chat_id),
    )


@messages_router.post(
    '/',
    description='Adds a new message to a chat.',
    status_code=status.HTTP_201_CREATED,
)
async def create_message(
    schema: CreateMessageSchema,
    service: ChatServiceDep,
) -> str:
    entity = schema.to_entity()
    await service.create_message(entity)
    return f'Message with id {entity.id} to chat with id {entity.chat_id} successfully created'


@messages_router.get(
    '/{message_id}',
    description='Retrieves a message by its ID.',
    status_code=status.HTTP_200_OK,
)
async def get_message(
    message_id: UUID,
    service: ChatServiceDep,
) -> Message:
    return await service.get_message(message_id)


@messages_router.delete(
    '/{message_id}',
    description='Deletes a message by its ID.',
    status_code=status.HTTP_200_OK,
)
async def delete_message(
    message_id: UUID,
    service: ChatServiceDep,
) -> str:
    await service.delete_message(message_id)
    return f'Message with id {message_id} successfully deleted'
