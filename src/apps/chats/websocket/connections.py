import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from fastapi import WebSocket

from src.apps.chats.websocket.schemas import (
    ErrorData,
    MessageReadData,
    TextMessageData,
    TypingIndicatorData,
    UserJoinedData,
    UserLeftData,
    WebSocketMessage,
    WebSocketMessageType,
)

logger = logging.getLogger(__name__)


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


@dataclass
class ConnectionManager(metaclass=SingletonMeta):
    connections_map: dict[UUID, list[WebSocket]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    async def accept_connection(self, websocket: WebSocket, key: UUID):
        logger.info("Accepting connection for key: %s", key)
        await websocket.accept()
        self.connections_map[key].append(websocket)

    async def remove_connection(self, websocket: WebSocket, key: UUID):
        logger.info("Removing connection for key: %s", key)
        self.connections_map[key].remove(websocket)

    async def send_message(self, key: UUID, message: WebSocketMessage):
        logger.info(
            "Sending message of type %s to all connections for key: %s",
            message.type,
            key,
        )
        message_json = message.model_dump_json()
        for websocket in self.connections_map[key]:
            await websocket.send_text(message_json)

    async def send_text_message(
        self, key: UUID, message_id: UUID, content: str, sender_id: int, chat_id: UUID
    ):
        logger.info("Sending text message to all connections for key: %s", key)
        message = WebSocketMessage(
            type=WebSocketMessageType.TEXT_MESSAGE,
            data=TextMessageData(
                message_id=message_id,
                content=content,
                sender_id=sender_id,
                chat_id=chat_id,
                created_at=datetime.now().isoformat(),
            ).model_dump(),
        )
        await self.send_message(key, message)

    async def send_message_read(self, key: UUID, message_id: UUID, user_id: int):
        logger.info(
            "Sending message read notification to all connections for key: %s", key
        )
        message = WebSocketMessage(
            type=WebSocketMessageType.MESSAGE_READ,
            data=MessageReadData(message_id=message_id, user_id=user_id).model_dump(),
        )
        await self.send_message(key, message)

    async def send_typing_indicator(self, key: UUID, user_id: int, is_typing: bool):
        logger.info(
            "Sending typing indicator for user with id '%s' in chat with id '%s'",
            user_id,
            key,
        )
        message = WebSocketMessage(
            type=WebSocketMessageType.TYPING_INDICATOR,
            data=TypingIndicatorData(user_id=user_id, is_typing=is_typing).model_dump(),
        )
        await self.send_message(key, message)

    async def send_user_joined(self, key: UUID, user_id: int, username: str = None):
        logger.info(
            "Sending user joined notification for user with id '%s' in chat with id '%s'",
            user_id,
            key,
        )
        message = WebSocketMessage(
            type=WebSocketMessageType.USER_JOINED,
            data=UserJoinedData(user_id=user_id, username=username).model_dump(),
        )
        await self.send_message(key, message)

    async def send_user_left(self, key: UUID, user_id: int, username: str = None):
        logger.info(
            "Sending user left notification for user with id '%s' in chat with id '%s'",
            user_id,
            key,
        )
        message = WebSocketMessage(
            type=WebSocketMessageType.USER_LEFT,
            data=UserLeftData(user_id=user_id, username=username).model_dump(),
        )
        await self.send_message(key, message)

    async def send_error(self, key: UUID, code: str, message: str):
        logger.info("Sending error message to all connections for key: %s", key)
        error_message = WebSocketMessage(
            type=WebSocketMessageType.ERROR,
            data=ErrorData(code=code, message=message).model_dump(),
        )
        await self.send_message(key, error_message)

    async def disconnect_all(self, key: UUID, reason: str):
        logger.info("Disconnecting all connections for key: %s", key)
        for websocket in self.connections_map[key]:
            await websocket.send_json({"message": reason})
            await websocket.close()
