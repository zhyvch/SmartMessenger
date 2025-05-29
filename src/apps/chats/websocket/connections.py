import logging
from uuid import UUID

from fastapi import WebSocket
from dataclasses import dataclass, field
from collections import defaultdict


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

    async def send_all(self, key: UUID, bytes_: bytes):
        logger.info('Sending bytes to all connections for key: %s', key)
        for websocket in self.connections_map[key]:
            await websocket.send_bytes(bytes_)

    async def disconnect_all(self, key: UUID, reason: str):
        logger.info('Disconnecting all connections for key: %s', key)
        for websocket in self.connections_map[key]:
            await websocket.send_json({'message': reason})
            await websocket.close()
