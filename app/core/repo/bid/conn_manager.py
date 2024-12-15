from typing import Dict, Set
from collections import defaultdict
from fastapi import WebSocket
import logging




class ConnectionManager:
    def __init__(self):
        self.groups: Dict[str, set] = defaultdict(set)
        self.logger = logging.getLogger(__name__)

    async def connect(self, websocket: WebSocket, group: str):
        if group in self.groups:
            await websocket.accept()
            self.groups[group].add(websocket)
            self.logger.info(f"User connected to group {group}. Total users: {len(self.groups[group])}")

    async def disconnect(self, websocket: WebSocket, group: str):
            self.groups[group].remove(websocket)
            self.logger.info(f"User disconnected from group {group}. Remaining users: {len(self.groups[group])}")

    
    async def broadcast(self, message: str, group: str):
        for connection in self.groups[group]:
            await connection.send_text(message)
        self.logger.info(f"Broadcast message to group {group}: {message}. Recipients: {len(self.groups[group])}")

    async def get_group_count(self, group: str):
            self.logger.debug(f"Getting count of users in group {group}")
            return len(self.groups[group])
