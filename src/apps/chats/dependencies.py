from typing import Annotated

from fastapi import Depends

from src.apps.chats.repositories import BaseChatRepository, BaseMessageRepository
from src.apps.chats.repositories import BeanieChatRepository, BeanieMessageRepository
from src.apps.chats.services import BaseChatService, ChatService
from src.apps.chats.websocket.connections import ConnectionManager


def get_chat_repo() -> BaseChatRepository:
    return BeanieChatRepository()


def get_message_repo() -> BaseMessageRepository:
    return BeanieMessageRepository()


def get_connection_manager() -> ConnectionManager:
    return ConnectionManager()


ChatRepositoryDep = Annotated[BaseChatRepository, Depends(get_chat_repo)]
MessageRepositoryDep = Annotated[BaseMessageRepository, Depends(get_message_repo)]
ConnectionManagerDep = Annotated[ConnectionManager, Depends(get_connection_manager)]


def get_chat_service(
    chat_repo: ChatRepositoryDep,
    message_repo: MessageRepositoryDep,
    connection_manager: ConnectionManagerDep,
) -> BaseChatService:
    return ChatService(chat_repo=chat_repo, message_repo=message_repo, connection_manager=connection_manager)


ChatServiceDep = Annotated[BaseChatService, Depends(get_chat_service)]
