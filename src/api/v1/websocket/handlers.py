import logging
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.api.v1.dependencies import ConnectionManagerDep

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket('/{chat_id}')
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: UUID,
    connection_manager: ConnectionManagerDep,
):
    await connection_manager.accept_connection(websocket=websocket, key=chat_id)
    await websocket.send_text(f'Successfully connected to chat {chat_id}')

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await connection_manager.remove_connection(websocket=websocket, key=chat_id)
