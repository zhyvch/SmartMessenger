import json
import logging
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from src.apps.chats.dependencies import ConnectionManagerDep, WebsocketChatMemberDep
from src.apps.chats.websocket.schemas import WebSocketMessageType

logger = logging.getLogger(__name__)
chats_ws_router = APIRouter()


@chats_ws_router.websocket("/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: UUID,
    chat_member: WebsocketChatMemberDep,
    connection_manager: ConnectionManagerDep,
):
    await connection_manager.accept_connection(websocket=websocket, key=chat_id)
    await connection_manager.send_user_joined(
        key=chat_id, user_id=chat_member.id, username=chat_member.username
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
                        key=chat_id, user_id=chat_member.id, is_typing=is_typing
                    )
                elif message_type == WebSocketMessageType.MESSAGE_READ:
                    message_id = message.get("data", {}).get("message_id")
                    if message_id:
                        await connection_manager.send_message_read(
                            key=chat_id,
                            message_id=UUID(message_id),
                            user_id=chat_member.id,
                        )
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received from user {chat_member.id}")
                await connection_manager.send_error(
                    key=chat_id, code="invalid_json", message="Invalid JSON format"
                )
            except ValidationError as e:
                logger.warning(
                    f"Validation error for message from user {chat_member.id}: {str(e)}"
                )
                await connection_manager.send_error(
                    key=chat_id,
                    code="validation_error",
                    message=f"Validation error: {str(e)}",
                )
            except Exception as e:
                logger.error(
                    f"Error processing message from user {chat_member.id}: {str(e)}"
                )
                await connection_manager.send_error(
                    key=chat_id,
                    code="server_error",
                    message="Server error processing message",
                )
    except WebSocketDisconnect:
        await connection_manager.remove_connection(websocket=websocket, key=chat_id)
        await connection_manager.send_user_left(
            key=chat_id, user_id=chat_member.id, username=chat_member.username
        )
