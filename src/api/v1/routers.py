from fastapi import APIRouter

from src.apps.ai.routers import ai_router
from src.apps.chats.routers import chats_router, messages_router
from src.apps.users.routers.auth import auth_router
from src.apps.users.routers.users import users_router
from src.apps.chats.websocket.routers import chats_ws_router


v1_router = APIRouter()
v1_router.include_router(chats_router, prefix='/chats', tags=['chats'])
v1_router.include_router(messages_router, prefix='/messages', tags=['messages'])
v1_router.include_router(auth_router, prefix='/auth', tags=['auth'])
v1_router.include_router(users_router, prefix='/users', tags=['users'])
v1_router.include_router(ai_router, prefix='/ai', tags=['ai'])


v1_ws_router = APIRouter()
v1_ws_router.include_router(chats_ws_router, prefix='/chats', tags=['chats'])
