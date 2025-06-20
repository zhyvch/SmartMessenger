# User Experience Implementation Guide

This guide provides detailed instructions for implementing the user experience enhancements in the improvement plan.

## 1. Add Endpoint to Retrieve All User Chats

**Current Issue**: There is no endpoint to retrieve all chats for the current user, which is essential for displaying a chat list in the UI.

**Implementation Steps**:

1. Add a new abstract method to `BaseChatRepository` in `src/apps/chats/repositories/base.py`:

```python
@abstractmethod
async def get_user_chats(self, user_id: int) -> list[Chat]:
    ...
```

2. Implement this method in `BeanieChatRepository` in `src/apps/chats/repositories/mongodb.py`:

```python
async def get_user_chats(self, user_id: int) -> list[Chat]:
    logger.info('Retrieving chats for user with id \'%s\'', user_id)
    chats = await self.model.find(
        In(self.model.member_ids, [user_id])
    ).to_list()
    return [self.converter.to_entity(chat) for chat in chats]
```

3. Add a new abstract method to `BaseChatService` in `src/apps/chats/services/base.py`:

```python
@abstractmethod
async def get_user_chats(self, user_id: int) -> list[Chat]:
    ...
```

4. Implement this method in `ChatService` in `src/apps/chats/services/chats.py`:

```python
async def get_user_chats(self, user_id: int) -> list[Chat]:
    logger.info('Retrieving chats for user with id \'%s\'', user_id)
    return await self.chat_repo.get_user_chats(user_id)
```

5. Add a new endpoint to `chats_router` in `src/apps/chats/routers.py`:

```python
@chats_router.get(
    '/',
    description='Retrieves all chats for the current user.',
    status_code=status.HTTP_200_OK,
)
async def get_user_chats(
    service: ChatServiceDep,
    current_user: CurrentUserDep
) -> list[Chat]:
    return await service.get_user_chats(current_user.id)
```

## 2. Add Message Read Status

**Current Issue**: The application doesn't track which messages have been read by users, which is important for chat applications.

**Implementation Steps**:

1. Update the `MessageModel` in `src/apps/chats/models.py` to track read status by user:

```python
class MessageModel(Document):
    id: UUID
    created_at: datetime
    updated_at: datetime
    content: str
    is_read: bool
    read_by: list[int] = []  # List of user IDs who have read the message
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
```

2. Update the `Message` entity in `src/apps/chats/entities.py`:

```python
class Message(BaseModel):
    id: UUID = Field(default_factory=uuid4, kw_only=True, exclude=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), kw_only=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), kw_only=True)
    content: str = Field(kw_only=True, max_length=255 * 1024)
    is_read: bool = Field(default=False, kw_only=True)
    read_by: list[int] = Field(default_factory=list, kw_only=True)
    sender_id: int = Field(kw_only=True)
    chat_id: UUID = Field(kw_only=True)
```

3. Add a new method to `BaseMessageRepository` in `src/apps/chats/repositories/base.py`:

```python
@abstractmethod
async def mark_message_as_read(self, message_id: UUID, user_id: int) -> None:
    ...
```

4. Implement this method in `BeanieMessageRepository` in `src/apps/chats/repositories/mongodb.py`:

```python
async def mark_message_as_read(self, message_id: UUID, user_id: int) -> None:
    logger.info('Marking message with id \'%s\' as read by user with id \'%s\'', message_id, user_id)
    message = await self.model.find_one(self.model.id == message_id)
    if message is None:
        logger.error('Message with id \'%s\' not found', message_id)
        raise MessageNotFoundException(message_id=message_id)

    if user_id not in message.read_by:
        message.read_by.append(user_id)
        message.is_read = True
        await message.save()
```

5. Add a new method to `BaseChatService` in `src/apps/chats/services/base.py`:

```python
@abstractmethod
async def mark_message_as_read(self, chat_id: UUID, message_id: UUID, user_id: int) -> None:
    ...
```

6. Implement this method in `ChatService` in `src/apps/chats/services/chats.py`:

```python
async def mark_message_as_read(self, chat_id: UUID, message_id: UUID, user_id: int) -> None:
    logger.info('Marking message with id \'%s\' as read by user with id \'%s\'', message_id, user_id)
    check_chat_exists = await self.get_chat(chat_id)

    message = await self.message_repo.get_message(message_id)
    if message.chat_id != chat_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Message with id {message_id} is not present in chat with id {chat_id}"
        )

    await self.message_repo.mark_message_as_read(message_id, user_id)
    
    # Notify other users that the message has been read
    await self.connection_manager.send_all(
        chat_id, 
        json.dumps({
            "type": "message_read",
            "message_id": str(message_id),
            "user_id": user_id
        }).encode()
    )
```

7. Add a new endpoint to `chats_router` in `src/apps/chats/routers.py`:

```python
@chats_router.post(
    '/{chat_id}/messages/{message_id}/read',
    description='Marks a message as read by the current user.',
    status_code=status.HTTP_200_OK,
)
async def mark_message_as_read(
    chat_id: UUID,
    message_id: UUID,
    service: ChatServiceDep,
    chat_member: ChatMemberDep
) -> str:
    await service.mark_message_as_read(chat_id, message_id, chat_member.id)
    return f'Message with id {message_id} marked as read by user with id {chat_member.id}'
```

## 3. Add User Typing Indicators

**Current Issue**: The application doesn't provide real-time typing indicators, which are important for a good chat experience.

**Implementation Steps**:

1. Add a new method to `ConnectionManager` in `src/apps/chats/websocket/connections.py`:

```python
async def send_typing_indicator(self, key: UUID, user_id: int, is_typing: bool):
    logger.info('Sending typing indicator for user with id \'%s\' in chat with id \'%s\'', user_id, key)
    message = json.dumps({
        "type": "typing_indicator",
        "user_id": user_id,
        "is_typing": is_typing
    })
    for websocket in self.connections_map[key]:
        await websocket.send_text(message)
```

2. Update the WebSocket endpoint in `src/apps/chats/websocket/routers.py` to handle typing indicator messages:

```python
@chats_ws_router.websocket('/{chat_id}')
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: UUID,
    chat_member: WebsocketChatMemberDep,
    connection_manager: ConnectionManagerDep,
):
    await connection_manager.accept_connection(websocket=websocket, key=chat_id)
    await websocket.send_text(f'Successfully connected to chat {chat_id}')

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "typing_indicator":
                    is_typing = message.get("is_typing", False)
                    await connection_manager.send_typing_indicator(chat_id, chat_member.id, is_typing)
            except json.JSONDecodeError:
                # Ignore invalid JSON
                pass
    except WebSocketDisconnect:
        await connection_manager.remove_connection(websocket=websocket, key=chat_id)
```

## Testing

After implementing these user experience enhancements, test the application to ensure everything works as expected:

1. Test the endpoint to retrieve all user chats:
```bash
curl -X GET "http://localhost:8000/api/v1/chats/" -H "Authorization: Bearer YOUR_TOKEN"
```

2. Test marking a message as read:
```bash
curl -X POST "http://localhost:8000/api/v1/chats/{chat_id}/messages/{message_id}/read" -H "Authorization: Bearer YOUR_TOKEN"
```

3. Test the typing indicators by connecting to the WebSocket endpoint and sending typing indicator messages:
```javascript
// In a browser or WebSocket client
const socket = new WebSocket("ws://localhost:8000/api/v1/chats/{chat_id}");
socket.onopen = () => {
  socket.send(JSON.stringify({
    type: "typing_indicator",
    is_typing: true
  }));
};
```