from collections import defaultdict
from typing import Optional, Dict, Set
from fastapi import WebSocket, WebSocketException
import logging


class ConnectionManager:
    def __init__(self):
        self.group_members: Dict[str, Set[WebSocket]] = {}
        self.group_meta_data: Dict[str, dict] = {} # Store additional data about a group
        self.group_objects: Dict[str, Object] = {}
        self.logger = logging.getLogger(__name__)

    async def connect(self, websocket: WebSocket, group_name: str):
        if group_name not in self.group_members:
            self.group_members[group_name] = set()
        self.group_members[group_name].add(websocket)
        self.logger.info(f"User created to group '{group_name}'.")
        return {"message": "Group created successfully."}

    async def join_group(self, websocket: WebSocket, group_name: str):
        if group_name in self.group_members:
            self.group_members[group_name].add(websocket)
            await websocket.send_json({"message": "Joined group successfully."})
        else:
            await websocket.close()
            return {"message": "Group does not exist."}

    async def get_group_count(self, group_name: str):
        if group_name in self.group_members:
            return len(self.group_members[group_name])
        else:
            return {"message": "Group does not exist."}

    async def disconnect(self, websocket: WebSocket, group_name: str):
        """
        Disconnects a single user (WebSocket) from a group.

        Args:
            websocket (WebSocket): The WebSocket connection to disconnect.
            group_name (str): The name of the group from which to disconnect the user.

        Returns:
            dict: A message indicating success or failure.
        """
        if group_name in self.group_members:
            if websocket in self.group_members[group_name]:
                # Remove the WebSocket from the group
                self.group_members[group_name].remove(websocket)
                # Close the WebSocket connection
                await websocket.close()
                self.logger.info(f"User disconnected from group '{group_name}'.")
                return {"message": "User disconnected successfully."}
            else:
                self.logger.warning(f"User not found in group '{group_name}'.")
                return {"message": "User not found in the specified group."}
        else:
            self.logger.warning(f"Group '{group_name}' does not exist.")
            return {"message": "Group does not exist."}

    async def disconnect_all(self, group_name: str):
        """
        Disconnects all users in the given group.

        :param group_name: Name of the group to disconnect all users from.
        :raises WebSocketException: If the group does not exist.
        """
        if group_name in self.group_members:
            for connections in self.group_members[group_name]:
                await connections.close()
            del self.group_members[group_name]
            del self.group_meta_data[group_name]
        else:
            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR,
                reason=f"{group_name} does not exist."
            )

            self.logginer.error(f"Group {group_name} does not exist.")

    async def broadcast(self,group_name: str, message: str):
        """
        Broadcasts a message to all users in a given group.

        :param group_name: Name of the group to broadcast the message to.
        :param message: The message to broadcast.
        :raises WebSocketException: If the group does not exist.
        """
        all_groups = list(self.group_members.keys())
        if group_name in all_groups:
            for connections in self.group_members[group_name]:
                await connections.send_text(message)
        else:
            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR,
                reason=f"{group_name} does not exist."
            )