from fastapi import APIRouter, WebSocket

router = APIRouter()


@router.websocket('/{chat_id}')
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: int,
):
    ...
