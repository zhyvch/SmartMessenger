import logging
from uuid import UUID

from fastapi import APIRouter, status

from src.api.schemas import ErrorSchema
from src.api.v1.dependencies import ChatServiceDep
from src.apps.chats.entities.chats import Chat, Message, ChatWithMessages
from src.apps.chats.schemas.chats import CreateChatSchema, CreateMessageSchema


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    '/chats',
    description='Creates a new chat.',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
    },
)
async def create_chat(
    schema: CreateChatSchema,
    service: ChatServiceDep,
) -> str:
    entity = schema.to_entity()
    await service.create_chat(entity)
    return f'Chat with id {entity.id} successfully created'


@router.get(
    '/chats/{chat_id}',
    description='Retrieves a chat by its ID.',
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
        status.HTTP_404_NOT_FOUND: {'model': ErrorSchema},
    },
)
async def get_chat(
    chat_id: UUID,
    service: ChatServiceDep,
) -> Chat:
    return await service.get_chat(chat_id)


@router.delete(
    '/chats/{chat_id}',
    description='Deletes a chat by its ID.',
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
        status.HTTP_404_NOT_FOUND: {'model': ErrorSchema},
    },
)
async def delete_chat(
    chat_id: UUID,
    service: ChatServiceDep,
) -> str:
    await service.delete_chat(chat_id)
    return f'Chat with id {chat_id} successfully deleted'


@router.get(
    '/chats/{chat_id}/messages',
    description='Retrieves all messages for a chat.',
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
        status.HTTP_404_NOT_FOUND: {'model': ErrorSchema},
    },
)
async def get_chat_messages(
    chat_id: UUID,
    service: ChatServiceDep,
) -> ChatWithMessages:
    return ChatWithMessages(
        chat=await service.get_chat(chat_id),
        messages=await service.get_messages(chat_id),
    )


@router.post(
    '/messages',
    description='Adds a new message to a chat.',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
        status.HTTP_404_NOT_FOUND: {'model': ErrorSchema},
    },
)
async def create_message(
    schema: CreateMessageSchema,
    service: ChatServiceDep,
) -> str:
    entity = schema.to_entity()
    await service.create_message(entity)
    return f'Message with id {entity.id} to chat with id {entity.chat_id} successfully created'


@router.get(
    '/messages/{message_id}',
    description='Retrieves a message by its ID.',
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
        status.HTTP_404_NOT_FOUND: {'model': ErrorSchema},
    },
)
async def get_message(
    message_id: UUID,
    service: ChatServiceDep,
) -> Message:
    return await service.get_message(message_id)


@router.delete(
    '/messages/{message_id}',
    description='Deletes a message by its ID.',
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
        status.HTTP_404_NOT_FOUND: {'model': ErrorSchema},
    },
)
async def delete_message(
    message_id: UUID,
    service: ChatServiceDep,
) -> str:
    await service.delete_message(message_id)
    return f'Message with id {message_id} successfully deleted'
