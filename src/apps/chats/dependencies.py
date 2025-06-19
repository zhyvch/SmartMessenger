from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Query, WebSocketException, status
from openai import OpenAI

from src.apps.ai.services import OpenAIService, UnsplashService
from src.apps.chats.entities import ChatPermissions
from src.apps.chats.repositories import (
    BaseChatPermissionsRepository,
    BaseChatRepository,
    BaseMessageRepository,
    BeanieChatPermissionsRepository,
    BeanieChatRepository,
    BeanieMessageRepository,
)
from src.apps.chats.schemas import Order, Pagination
from src.apps.chats.services import BaseChatService, ChatService
from src.apps.chats.websocket.connections import ConnectionManager
from src.apps.users.dependencies import CurrentWebsocketUserDep
from src.apps.users.models import User
from src.apps.users.routers.auth import get_current_user
from src.settings.config import settings


def pagination_params(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    ordering: Order = Order.ASC,
) -> Pagination:
    if ordering not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be either 'asc' or 'desc'",
        )

    return Pagination(limit=limit, offset=offset, ordering=ordering)


PaginationDep = Annotated[Pagination, Depends(pagination_params)]


def get_chat_repo() -> BaseChatRepository:
    return BeanieChatRepository()


def get_message_repo() -> BaseMessageRepository:
    return BeanieMessageRepository()


def get_chat_permissions_repo() -> BaseChatPermissionsRepository:
    return BeanieChatPermissionsRepository()


def get_connection_manager() -> ConnectionManager:
    return ConnectionManager()


ChatRepositoryDep = Annotated[BaseChatRepository, Depends(get_chat_repo)]
MessageRepositoryDep = Annotated[BaseMessageRepository, Depends(get_message_repo)]
ChatPermissionsRepositoryDep = Annotated[
    BaseChatPermissionsRepository, Depends(get_chat_permissions_repo)
]
ConnectionManagerDep = Annotated[ConnectionManager, Depends(get_connection_manager)]

openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
ai_service = OpenAIService(client=openai_client)
unsplash_service = UnsplashService(access_key=settings.UNSPLASH_ACCESS_KEY)


def get_chat_service(
    chat_repo: ChatRepositoryDep,
    message_repo: MessageRepositoryDep,
    chat_permissions_repo: ChatPermissionsRepositoryDep,
    connection_manager: ConnectionManagerDep,
) -> BaseChatService:
    return ChatService(
        chat_repo=chat_repo,
        message_repo=message_repo,
        chat_permissions_repo=chat_permissions_repo,
        connection_manager=connection_manager,
        ai_service=ai_service,
        unsplash_service=unsplash_service,
    )


ChatServiceDep = Annotated[BaseChatService, Depends(get_chat_service)]

CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def check_chat_member(
    chat_id: UUID, chat_repo: ChatRepositoryDep, current_user: CurrentUserDep
) -> User:
    chat = await chat_repo.get_chat(chat_id)
    if current_user.id not in chat.member_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of this chat",
        )

    return current_user


ChatMemberDep = Annotated[User, Depends(check_chat_member)]


async def check_websocket_chat_member(
    chat_id: UUID, chat_repo: ChatRepositoryDep, current_user: CurrentWebsocketUserDep
) -> User:
    chat = await chat_repo.get_chat(chat_id)
    if current_user.id not in chat.member_ids:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="User is not a member of this chat",
        )

    return current_user


WebsocketChatMemberDep = Annotated[User, Depends(check_websocket_chat_member)]


async def check_chat_owner(
    chat_id: UUID, chat_repo: ChatRepositoryDep, current_user: CurrentUserDep
) -> User:
    chat = await chat_repo.get_chat(chat_id)
    if chat.is_group and current_user.id != chat.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an owner of this chat",
        )

    return current_user


ChatOwnerDep = Annotated[User, Depends(check_chat_owner)]


async def check_send_permission(
    chat_id: UUID,
    chat_permissions_repo: ChatPermissionsRepositoryDep,
    current_member: ChatMemberDep,
) -> User:
    permissions = await chat_permissions_repo.get_user_chat_permissions(
        chat_id=chat_id, user_id=current_member.id
    )
    if not permissions.can_send_messages:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User cannot send messages in this chat",
        )

    return current_member


SendPermissionDep = Annotated[ChatPermissions, Depends(check_send_permission)]


async def check_change_permission(
    chat_id: UUID,
    user_id: int,
    chat_permissions_repo: ChatPermissionsRepositoryDep,
    current_member: ChatMemberDep,
) -> User:
    if user_id == current_member.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User cannot change own permissions in chats",
        )

    permissions = await chat_permissions_repo.get_user_chat_permissions(
        chat_id=chat_id, user_id=current_member.id
    )
    if not permissions.can_change_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User cannot change other users permissions in this chat",
        )

    return current_member


ChangePermissionDep = Annotated[ChatPermissions, Depends(check_change_permission)]


async def check_remove_members_permission(
    chat_id: UUID,
    user_id: int,
    chat_permissions_repo: ChatPermissionsRepositoryDep,
    current_member: ChatMemberDep,
) -> User:
    if user_id == current_member.id:
        return current_member

    permissions = await chat_permissions_repo.get_user_chat_permissions(
        chat_id=chat_id, user_id=current_member.id
    )
    if not permissions.can_remove_members:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User cannot remove other members in this chat",
        )

    return current_member


RemoveMembersPermissionDep = Annotated[
    ChatPermissions, Depends(check_remove_members_permission)
]


async def check_delete_messages_permission(
    chat_id: UUID,
    message_id: UUID,
    message_repo: MessageRepositoryDep,
    chat_permissions_repo: ChatPermissionsRepositoryDep,
    current_member: ChatMemberDep,
) -> User:
    message = await message_repo.get_message(message_id)

    if message.sender_id == current_member.id:
        return current_member

    permissions = await chat_permissions_repo.get_user_chat_permissions(
        chat_id=chat_id, user_id=current_member.id
    )
    if not permissions.can_delete_other_messages:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User cannot delete other members messages in this chat",
        )

    return current_member


DeleteMessagesPermissionDep = Annotated[
    ChatPermissions, Depends(check_delete_messages_permission)
]
