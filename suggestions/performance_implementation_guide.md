# Performance Implementation Guide

This guide provides detailed instructions for implementing the performance improvements in the improvement plan.

## 1. Add Pagination for Chat Messages

**Current Issue**: The endpoint to retrieve chat messages doesn't support pagination, which could lead to performance issues for chats with many messages.

**Implementation Steps**:

1. Update the chat messages endpoint in `src/apps/chats/routers.py`:

```python
@chats_router.get(
    '/{chat_id}/messages',
    description='Retrieves messages for a chat with pagination.',
    status_code=status.HTTP_200_OK,
)
async def get_chat_messages(
    chat_id: UUID,
    service: ChatServiceDep,
    chat_member: ChatMemberDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> ChatWithMessages:
    return ChatWithMessages(
        chat=await service.get_chat(chat_id),
        messages=await service.get_messages(chat_id, skip=skip, limit=limit),
    )
```

2. Update the `get_messages` method in `src/apps/chats/services/chats.py`:

```python
async def get_messages(self, chat_id: UUID, skip: int = 0, limit: int = 50) -> list[Message]:
    """Get messages for a chat with pagination."""
    messages = await self.message_repo.get_messages(chat_id=chat_id, skip=skip, limit=limit)
    return [message.to_entity() for message in messages]
```

3. Update the repository method in `src/apps/chats/repositories/mongodb.py`:

```python
async def get_messages(self, chat_id: UUID, skip: int = 0, limit: int = 50) -> list[MessageModel]:
    """Get messages for a chat with pagination."""
    return await MessageModel.find(
        MessageModel.chat_id == chat_id
    ).sort(-MessageModel.created_at).skip(skip).limit(limit).to_list()
```

## 2. Add Indexes to MongoDB Collections

**Current Issue**: MongoDB collections don't have indexes, which could lead to slow queries.

**Implementation Steps**:

1. Update the MongoDB models in `src/apps/chats/models.py` to include indexes:

```python
class ChatModel(Document):
    id: UUID
    created_at: datetime
    updated_at: datetime
    name: str
    is_group: bool
    owner_id: int
    member_ids: list[int]

    class Settings:
        name = 'chats'
        indexes = [
            "id",
            "owner_id",
            "member_ids",
            ("created_at", -1),  # Descending index on created_at
        ]


class MessageModel(Document):
    id: UUID
    created_at: datetime
    updated_at: datetime
    content: str
    is_read: bool
    sender_id: int
    chat_id: UUID

    class Settings:
        name = 'messages'
        indexes = [
            "id",
            "chat_id",
            "sender_id",
            ("chat_id", "created_at", -1),  # Compound index for efficient chat message queries
        ]


class ChatPermissionsModel(Document):
    id: UUID
    chat_id: UUID
    user_id: int
    can_send_messages: bool = True
    can_change_permissions: bool = False
    can_remove_members: bool = False
    can_delete_other_messages: bool = False

    class Settings:
        name = 'chat_permissions'
        indexes = [
            "id",
            "chat_id",
            "user_id",
            ("chat_id", "user_id"),  # Compound index for efficient permission lookups
        ]
```

## 3. Optimize WebSocket Message Broadcasting

**Current Issue**: The current WebSocket implementation sends messages as raw bytes, which is not ideal for structured data. It also doesn't handle different message types efficiently.

**Implementation Steps**:

1. Create a new file `src/apps/chats/websocket/schemas.py` to define WebSocket message schemas:

```python
from enum import Enum
from typing import Optional, Any, Dict, List
from uuid import UUID
from pydantic import BaseModel, Field


class WebSocketMessageType(str, Enum):
    TEXT_MESSAGE = "text_message"
    MESSAGE_READ = "message_read"
    TYPING_INDICATOR = "typing_indicator"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    ERROR = "error"


class WebSocketMessage(BaseModel):
    type: WebSocketMessageType
    data: Dict[str, Any]


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
    username: Optional[str] = None


class UserLeftData(BaseModel):
    user_id: int
    username: Optional[str] = None


class ErrorData(BaseModel):
    code: str
    message: str
```

2. Update the `ConnectionManager` in `src/apps/chats/websocket/connections.py` to use the new message schemas:

```python
import json
import logging
from uuid import UUID
from datetime import datetime

from fastapi import WebSocket
from dataclasses import dataclass, field
from collections import defaultdict

from src.apps.chats.websocket.schemas import (
    WebSocketMessage,
    WebSocketMessageType,
    TextMessageData,
    MessageReadData,
    TypingIndicatorData,
    UserJoinedData,
    UserLeftData,
    ErrorData
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
        logger.info('Accepting connection for key: %s', key)
        await websocket.accept()
        self.connections_map[key].append(websocket)

    async def remove_connection(self, websocket: WebSocket, key: UUID):
        logger.info('Removing connection for key: %s', key)
        self.connections_map[key].remove(websocket)

    async def send_message(self, key: UUID, message: WebSocketMessage):
        logger.info('Sending message of type %s to all connections for key: %s', message.type, key)
        message_json = message.model_dump_json()
        for websocket in self.connections_map[key]:
            await websocket.send_text(message_json)

    async def send_text_message(self, key: UUID, message_id: UUID, content: str, sender_id: int, chat_id: UUID):
        logger.info('Sending text message to all connections for key: %s', key)
        message = WebSocketMessage(
            type=WebSocketMessageType.TEXT_MESSAGE,
            data=TextMessageData(
                message_id=message_id,
                content=content,
                sender_id=sender_id,
                chat_id=chat_id,
                created_at=datetime.now().isoformat()
            ).model_dump()
        )
        await self.send_message(key, message)

    async def send_message_read(self, key: UUID, message_id: UUID, user_id: int):
        logger.info('Sending message read notification to all connections for key: %s', key)
        message = WebSocketMessage(
            type=WebSocketMessageType.MESSAGE_READ,
            data=MessageReadData(
                message_id=message_id,
                user_id=user_id
            ).model_dump()
        )
        await self.send_message(key, message)

    async def send_typing_indicator(self, key: UUID, user_id: int, is_typing: bool):
        logger.info('Sending typing indicator for user with id \'%s\' in chat with id \'%s\'', user_id, key)
        message = WebSocketMessage(
            type=WebSocketMessageType.TYPING_INDICATOR,
            data=TypingIndicatorData(
                user_id=user_id,
                is_typing=is_typing
            ).model_dump()
        )
        await self.send_message(key, message)

    async def send_user_joined(self, key: UUID, user_id: int, username: str = None):
        logger.info('Sending user joined notification for user with id \'%s\' in chat with id \'%s\'', user_id, key)
        message = WebSocketMessage(
            type=WebSocketMessageType.USER_JOINED,
            data=UserJoinedData(
                user_id=user_id,
                username=username
            ).model_dump()
        )
        await self.send_message(key, message)

    async def send_user_left(self, key: UUID, user_id: int, username: str = None):
        logger.info('Sending user left notification for user with id \'%s\' in chat with id \'%s\'', user_id, key)
        message = WebSocketMessage(
            type=WebSocketMessageType.USER_LEFT,
            data=UserLeftData(
                user_id=user_id,
                username=username
            ).model_dump()
        )
        await self.send_message(key, message)

    async def send_error(self, key: UUID, code: str, message: str):
        logger.info('Sending error message to all connections for key: %s', key)
        error_message = WebSocketMessage(
            type=WebSocketMessageType.ERROR,
            data=ErrorData(
                code=code,
                message=message
            ).model_dump()
        )
        await self.send_message(key, error_message)

    async def disconnect_all(self, key: UUID, reason: str):
        logger.info('Disconnecting all connections for key: %s', key)
        for websocket in self.connections_map[key]:
            await websocket.send_json({'message': reason})
            await websocket.close()
```

3. Update the WebSocket endpoint in `src/apps/chats/websocket/routers.py` to use the new message schemas:

```python
import json
import logging
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from src.apps.chats.dependencies import ConnectionManagerDep, WebsocketChatMemberDep
from src.apps.chats.websocket.schemas import WebSocketMessageType

logger = logging.getLogger(__name__)
chats_ws_router = APIRouter()


@chats_ws_router.websocket('/{chat_id}')
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: UUID,
    chat_member: WebsocketChatMemberDep,
    connection_manager: ConnectionManagerDep,
):
    await connection_manager.accept_connection(websocket=websocket, key=chat_id)
    await connection_manager.send_user_joined(
        key=chat_id,
        user_id=chat_member.id,
        username=chat_member.username
    )

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == WebSocketMessageType.TYPING_INDICATOR:
                    is_typing = message.get("data", {}).get("is_typing", False)
                    await connection_manager.send_typing_indicator(
                        key=chat_id,
                        user_id=chat_member.id,
                        is_typing=is_typing
                    )
                elif message_type == WebSocketMessageType.MESSAGE_READ:
                    message_id = message.get("data", {}).get("message_id")
                    if message_id:
                        await connection_manager.send_message_read(
                            key=chat_id,
                            message_id=UUID(message_id),
                            user_id=chat_member.id
                        )
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received from user {chat_member.id}")
                await connection_manager.send_error(
                    key=chat_id,
                    code="invalid_json",
                    message="Invalid JSON format"
                )
            except ValidationError as e:
                logger.warning(f"Validation error for message from user {chat_member.id}: {str(e)}")
                await connection_manager.send_error(
                    key=chat_id,
                    code="validation_error",
                    message=f"Validation error: {str(e)}"
                )
            except Exception as e:
                logger.error(f"Error processing message from user {chat_member.id}: {str(e)}")
                await connection_manager.send_error(
                    key=chat_id,
                    code="server_error",
                    message="Server error processing message"
                )
    except WebSocketDisconnect:
        await connection_manager.remove_connection(websocket=websocket, key=chat_id)
        await connection_manager.send_user_left(
            key=chat_id,
            user_id=chat_member.id,
            username=chat_member.username
        )
```

4. Update the `create_message` method in `ChatService` to use the new message format:

```python
async def create_message(self, message: Message) -> None:
    logger.info('Creating message to chat with id \'%s\'', message.chat_id)
    check_chat_exists = await self.get_chat(message.chat_id)

    await self.message_repo.add_message(message)
    
    # Use the new structured message format
    await self.connection_manager.send_text_message(
        key=message.chat_id,
        message_id=message.id,
        content=message.content,
        sender_id=message.sender_id,
        chat_id=message.chat_id
    )

    # Handle AI and photo commands as before...
```

## Testing

After implementing these performance improvements, test the application to ensure everything works as expected:

1. Test the pagination for chat messages by creating a chat with many messages and retrieving them with different pagination parameters:
```bash
curl -X GET "http://localhost:8000/api/v1/chats/{chat_id}/messages?skip=0&limit=10" -H "Authorization: Bearer YOUR_TOKEN"
curl -X GET "http://localhost:8000/api/v1/chats/{chat_id}/messages?skip=10&limit=10" -H "Authorization: Bearer YOUR_TOKEN"
```

2. Monitor the MongoDB query performance before and after adding indexes to verify the improvement.

3. Test the optimized WebSocket message broadcasting:
```javascript
// In a browser or WebSocket client
const socket = new WebSocket("ws://localhost:8000/api/v1/chats/{chat_id}");
socket.onopen = () => {
  // Send a typing indicator
  socket.send(JSON.stringify({
    type: "typing_indicator",
    data: {
      is_typing: true
    }
  }));
  
  // Send a message read notification
  socket.send(JSON.stringify({
    type: "message_read",
    data: {
      message_id: "550e8400-e29b-41d4-a716-446655440001"
    }
  }));
};

socket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log("Received message type:", message.type);
  console.log("Message data:", message.data);
};
```