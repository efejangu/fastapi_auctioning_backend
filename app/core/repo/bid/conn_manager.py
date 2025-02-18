
from asyncio import Lock
from fastapi import WebSocket
from typing import Dict, Optional
import logging

class ConnectionManager:
    def __init__(self):
        self.group_members: Dict[str, Dict[str, WebSocket]] = {}
        self.group_admins: Dict[str, str] = {}
        self.group_objects: Dict[str, AuctionGroup] = {}
        self.logger = logging.getLogger(__name__)
        self.lock = Lock()  # Initialize the lock

    async def connect(self, websocket: WebSocket, group_name: str, id: str):
        async with self.lock:  # Acquire the lock
            if group_name not in self.group_members.keys():
                self.group_members[group_name] = {id: websocket}
                self.group_admins[group_name] = id
                self.logger.info(f"User {id} created group '{group_name}'.")
            else:
                await websocket.send_text("Group already exists.")
                await websocket.close()

    async def join_group(self, websocket: WebSocket, group_name: str, id: str):
        async with self.lock:  # Acquire the lock
            if group_name in self.group_members:
                self.group_members[group_name].update({id: websocket})
                self.logger.info(f"User {id} joined group {group_name}.")
            else:
                await websocket.send_text("Group does not exist.")
                await websocket.close()

    async def disconnect(self, websocket: WebSocket, group_name: str, id: str):
        async with self.lock:  # Acquire the lock
            if group_name in self.group_members and id in self.group_members[group_name]:
                self.group_members[group_name][id].send_text("User disconnected.")
                await self.group_members[group_name][id].close()
                del self.group_members[group_name][id]
                self.logger.info(f"User {id} disconnected from group {group_name}.")
                return {"message": "User disconnected."}
            return {"message": "User not found in group."}

    async def broadcast(self, group_name: str, message: str):
        async with self.lock:  # Acquire the lock
            if group_name in self.group_members:
                for member_id, websocket in self.group_members[group_name].items():
                    try:
                        await websocket.send_text(message)
                    except Exception as e:
                        self.logger.error(f"Failed to send message to user {member_id}: {e}")
                self.logger.info(f"Message broadcasted to group {group_name}.")
            else:
                raise WebSocketException(
                    code=status.WS_1011_INTERNAL_ERROR,
                    reason=f"Group {group_name} does not exist."
                )

    async def get_admin_websocket(self, group_name: str, id: str) -> WebSocket:
        async with self.lock:  # Acquire the lock
            if group_name in self.group_members and id in self.group_members[group_name]:
                return self.group_members[group_name][id]
            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR,
                reason=f"User {id} not found in group {group_name}."
            )
    async def get_user_websocket(self, group_name: str, id: str) -> WebSocket:
        async with self.lock:  # Acquire the lock
            if group_name in self.group_members and id in self.group_members[group_name]:
                return self.group_members[group_name][id]
            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR,
                reason=f"User {id} not found in group {group_name}."
            )
