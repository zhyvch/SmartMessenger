from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class WebSocketMessageType(str, Enum):
    TEXT_MESSAGE = "text_message"
    MESSAGE_READ = "message_read"
    TYPING_INDICATOR = "typing_indicator"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    ERROR = "error"


class WebSocketMessage(BaseModel):
    type: WebSocketMessageType
    data: dict[str, Any]


class TextMessageData(BaseModel):
    message_id: UUID
    content: str
    sender_id: int
    chat_id: UUID
    created_at: str


class MessageReadData(BaseModel):
    message_id: UUID
    user_id: int


class TypingIndicatorData(BaseModel):
    user_id: int
    is_typing: bool


class UserJoinedData(BaseModel):
    user_id: int
    username: str | None = None


class UserLeftData(BaseModel):
    user_id: int
    username: str | None = None


class ErrorData(BaseModel):
    code: str
    message: str
