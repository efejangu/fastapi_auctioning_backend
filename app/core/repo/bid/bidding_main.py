"""
Main module for bidding operations in the bidding application.

This module serves as the entry point for core bidding functionality,
coordinating interactions between different components of the bidding system.
"""
from typing import Set
from fastapi import WebSocket
from .bidding_logic import AuctionGroup
from .conn_manager import ConnectionManager
from fastapi import WebSocket, HTTPException
from fastapi.responses import JSONResponse
from uuid import uuid4
import logging
from app.models import BidingHistory

class BiddingMain:
    def __init__(self, connection_manager=None):
        self.connection_manager = connection_manager
        self.logger = logging.getLogger(__name__)
    async def create_group(self, websocket: WebSocket, group_name: str, item:str, target_price: float):
        """Creates a new group. Returns True on success, False if the group already exists."""
        admin_id = str(uuid4())
        await self.connection_manager.connect(websocket, group_name, admin_id)
        group_obj = AuctionGroup(group_name, item, self.connection_manager, target_price)
        self.connection_manager.group_objects[group_name] = group_obj

        await websocket.send_json({"message": "Group created successfully.", "id": admin_id})
        self.logger.info(f"User created group {group_name}")

    async def disconnect(self, websocket: WebSocket, group_name: str, id: str):
        await self.connection_manager.disconnect(websocket, group_name, id)
        await self.logger.info(f"User disconnected from group {group_name}")
        
    async def place_bid(self, id: str, bid: float, bidder_name: str, group_name: str):
        #Warns admin they cannot place bids

        if id == self.connection_manager.group_admins[group_name]:
            self.connection_manager.get_admin_websocket(id).send_json(
                {"message": "admins can't place bids.", "id": id}
            )
            return
        if group_name not in list(self.connection_manager.group_objects.keys()):
            raise ValueError(f"Group '{group_name}' does not exist.")
        if id not in self.connection_manager.group_members[group_name].keys():
            #TO-DO Disconnect user
            raise ValueError(f"User ID '{id}' is not a member of group '{group_name}'.")

        group_obj = self.connection_manager.group_objects[group_name]
        connection = self.connection_manager.group_members[group_name][id]
        await group_obj.place_bid(connection, bid, bidder_name)

    async def join_group(self, websocket: WebSocket, group_name: str, token=None):
        member_id = str(uuid4())
        await self.connection_manager.join_group(websocket, group_name, member_id)
        await websocket.send_json({"message": "Joined group successfully.", "id":member_id})

    async def close_auction(self, id: str,group_name: str):
        if (
          group_name in list(self.connection_manager.group_admins.keys())
          and id == self.connection_manager.group_admins[group_name]
        ):
            await self.connection_manager.group_objects[group_name].close_auction()


    async def bidding_status(self, group_name: str):
         group_obj = self.connection_manager.group_objects[group_name]
         return group_obj.stack.peek()


    async def get_groups(self):

        groups = []
        # If there are no groups, then there is nothing to get
        if len(self.connection_manager.group_members) == 0:
            groups.append( {"message":"No group data available"})
            return groups

        # Initialize the dictionary to return

        # Iterate over the group_members and group_objects pairs
        for group_name in self.connection_manager.group_members:
            #get the group object with the same name
            auction_group_object = self.connection_manager.group_objects[group_name]
            groups.append({
                "active_bidders": len(self.connection_manager.group_members[group_name]),
                "group_name": auction_group_object.group_name,
                "item": auction_group_object.item_name,
                "current_highest_bid": auction_group_object.highest_bid
            })

        return groups




        
