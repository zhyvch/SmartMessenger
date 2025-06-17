import logging
from uuid import UUID

from fastapi import APIRouter, status

from apps.users.dependencies import CheckUserExistsByIDDep
from src.apps.chats.dependencies import ChatServiceDep, ChatMemberDep, ChatOwnerDep, SendPermissionDep, \
    CurrentUserDep, RemoveMembersPermissionDep, DeleteMessagesPermissionDep, ChangePermissionDep
from src.apps.chats.entities import Chat, Message, ChatWithMessages
from src.apps.chats.schemas import CreateChatSchema, CreateMessageSchema, UpdateChatPermissionsSchema

logger = logging.getLogger(__name__)
chats_router = APIRouter()


@chats_router.post(
    '/private/{user_id}',
    description='Creates a new private chat.',
    status_code=status.HTTP_201_CREATED,
)
async def create_private_chat(
    schema: CreateChatSchema,
    user_id: int,
    service: ChatServiceDep,
    current_user: CurrentUserDep,
    check_user: CheckUserExistsByIDDep
) -> str:
    entity = schema.to_entity(owner_id=current_user.id, is_group=False)
    await service.create_private_chat(chat=entity, other_user_id=user_id)
    return f'Private chat with id {entity.id} successfully created'


@chats_router.post(
    '/group',
    description='Creates a new group chat.',
    status_code=status.HTTP_201_CREATED,
)
async def create_group_chat(
    schema: CreateChatSchema,
    service: ChatServiceDep,
    current_user: CurrentUserDep,
) -> str:
    entity = schema.to_entity(owner_id=current_user.id, is_group=True)
    await service.create_group_chat(chat=entity)
    return f'Group chat with id {entity.id} successfully created'


@chats_router.get(
    '/{chat_id}',
    description='Retrieves a chat by its ID.',
    status_code=status.HTTP_200_OK,
)
async def get_chat(
    chat_id: UUID,
    service: ChatServiceDep,
    chat_member: ChatMemberDep
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
    chat_owner: ChatOwnerDep
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
    chat_member: ChatMemberDep
) -> ChatWithMessages:
    return ChatWithMessages(
        chat=await service.get_chat(chat_id),
        messages=await service.get_messages(chat_id),
    )


@chats_router.post(
    '/{chat_id}/messages',
    description='Adds a new message to a chat.',
    status_code=status.HTTP_201_CREATED,
)
async def create_message(
    chat_id: UUID,
    schema: CreateMessageSchema,
    service: ChatServiceDep,
    chat_member: SendPermissionDep
) -> str:
    entity = schema.to_entity(chat_id=chat_id, sender_id=chat_member.id)
    await service.create_message(entity)
    return f'Message with id {entity.id} to chat with id {entity.chat_id} successfully created'


@chats_router.get(
    '/{chat_id}/messages/{message_id}',
    description='Retrieves a message by its ID.',
    status_code=status.HTTP_200_OK,
)
async def get_message(
    chat_id: UUID,
    message_id: UUID,
    service: ChatServiceDep,
    chat_member: ChatMemberDep
) -> Message:
    return await service.get_message(chat_id, message_id)


@chats_router.delete(
    '/{chat_id}/messages/{message_id}',
    description='Deletes a message by its ID.',
    status_code=status.HTTP_200_OK,
)
async def delete_message(
    chat_id: UUID,
    message_id: UUID,
    service: ChatServiceDep,
    chat_member: DeleteMessagesPermissionDep
) -> str:
    await service.delete_message(chat_id, message_id)
    return f'Message with id {message_id} successfully deleted'


@chats_router.post(
    '/{chat_id}/members',
    description='Adds new chat member.',
    status_code=status.HTTP_200_OK,
)
async def add_chat_member(
    chat_id: UUID,
    user_id: int,
    service: ChatServiceDep,
    chat_member: ChatMemberDep,
    check_user: CheckUserExistsByIDDep
) -> str:
    await service.add_chat_member(chat_id=chat_id, user_id=user_id)
    return f'User with id {user_id} successfully added to chat with id {chat_id}'


@chats_router.delete(
    '/{chat_id}/members/{user_id}',
    description='Removes user from chat.',
    status_code=status.HTTP_200_OK,
)
async def remove_chat_member(
    chat_id: UUID,
    user_id: int,
    service: ChatServiceDep,
    chat_member: RemoveMembersPermissionDep,
    check_user: CheckUserExistsByIDDep
) -> str:
    await service.remove_chat_member(chat_id=chat_id, user_id=user_id)
    return f'User with id {user_id} successfully removed from chat with id {chat_id}'


@chats_router.patch(
    '/{chat_id}/members/{user_id}/permissions',
    description='Updates user chat permissions.',
    status_code=status.HTTP_200_OK,
)
async def update_user_chat_permissions(
    chat_id: UUID,
    user_id: int,
    new_chat_permissions: UpdateChatPermissionsSchema,
    service: ChatServiceDep,
    chat_member: ChangePermissionDep,
    check_user: CheckUserExistsByIDDep
) -> str:
    await service.update_user_chat_permissions(
        chat_id=chat_id,
        user_id=user_id,
        new_chat_permissions=new_chat_permissions
    )
    return f'Chat permissions for user with id {user_id} successfully changed in chat with id {chat_id}'
