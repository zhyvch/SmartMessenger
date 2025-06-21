from uuid import UUID

from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

from src.apps.chats.dependencies import ConnectionManagerDep, WebsocketChatMemberDep

chats_ws_router = APIRouter()


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
