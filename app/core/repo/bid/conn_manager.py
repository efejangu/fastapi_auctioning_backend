from collections import defaultdict
from fastapi import WebSocket
import logging





class ConnectionManager:
    def __init__(self):
        self.groups = defaultdict(lambda: {"connections": set()})
        self.logger = logging.getLogger(__name__)

    async def connect(self, websocket: WebSocket, group: str):
        try:
            if group in self.groups:
                await websocket.accept()
                self.groups[group]["connections"].add(websocket)
                self.logger.info(f"User connected to auction {group}. Total users: {len(self.groups[group]['connections'])}")
            else:
                raise ValueError(f"Group {group} does not exist")
        except Exception as e:
            self.logger.error(f"Error connecting to group {group}: {str(e)}")
            raise

    async def disconnect(self, websocket: WebSocket, group: str):
        try:
            if group in self.groups and websocket in self.groups[group]["connections"]:
                self.groups[group]["connections"].remove(websocket)
                self.logger.info(f"User disconnected from group {group}. Remaining users: {len(self.groups[group]['connections'])}")
        except Exception as e:
            self.logger.error(f"Error disconnecting from group {group}: {str(e)}")

    async def disconnect_all(self, group: str):
        try:
            if group in self.groups:
                connections = self.groups[group]["connections"].copy()
                for websocket in connections:
                    await self.disconnect(websocket, group)
                del self.groups[group]
                self.logger.info(f"All users disconnected and group {group} removed")
        except Exception as e:
            self.logger.error(f"Error disconnecting all users from group {group}: {str(e)}")
            raise

    async def broadcast(self, message: str, group: str):
        for connection in self.groups[group]["connections"]:
            await connection.send_text(message)
        self.logger.info(f"Broadcast message to group {group}: {message}. Recipients: {len(self.groups[group]['connections'])}")

    async def get_group_count(self, group: str):
            self.logger.debug(f"Getting count of users in group {group}")
            return len(self.groups[group]["connections"])
