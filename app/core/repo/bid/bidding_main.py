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

class BiddingMain:
    def __init__(self, connection_manager=None):
        self.connection_manager = connection_manager

    async def create_group(self, websocket: WebSocket, group_name: str, target_price: float):
        """Creates a new group. Returns True on success, False if the group already exists."""
        if group_name in self.connection_manager.group_members:
            return {"message": "Group name already exists, try a different name."} # Group already exists

        await self.connection_manager.connect(websocket, group_name)
        group_obj = AuctionGroup(group_name, self.connection_manager, target_price)
        self.connection_manager.group_objects[group_name] = group_obj
        await websocket.accept()

        await self.logger.info(f"User created group {group_name}")
        return {"message": "Group created successfully."}


    async def disconnect(self, websocket: WebSocket, group_name: str):
        await self.connection_manager.disconnect(websocket, group_name)
        
    async def place_bid(self, websocket: WebSocket, bid: float, bidder_name: str, group_name: str):
        if group_name not in self.connection_manager.groups:
            raise HTTPException(status_code=404, detail="Group not found")
        group_obj = self.connection_manager.group_objects[group_name]
        await group_obj.place_bid(websocket, bid, bidder_name)

    async def join_group(self, websocket: WebSocket, group_name: str, token=None):
        await websocket.accept()

        
        await websocket.send_json({"message": "Joined group successfully."})
        await self.connection_manager.join_group(websocket, group_name,)

    async def close_auction(self, group_name: str):
        group_obj = self.connection_manager.group_objects[group_name]
        #fix 45
        await get_group.close_auction()

    async def bidding_status(self, group_name: str):
         group_obj = self.connection_manager.group_objects[group_name]
         return group_obj.stack.peek()

    async def get_groups(self):
        # If there are no groups, then there is nothing to get
        if len(self.connection_manager.group_members) == 0:
            return {"message":"No group data available"}

        # Initialize the dictionary to return
        groups = {}

        # Iterate over the group_members and group_objects pairs
        for group_name in self.connection_manager.group_members:
            #get the group object with the same name
            auction_group_object = self.connection_manager.group_objects[group_name]
            groups[group_name] = {
                "active_bidders": len(self.connection_manager.group_members[group_name]),
                "group_name": auction_group_object.group_name,
                "current_highest_bid": auction_group_object.highest_bid
            }

        return JSONResponse(content=groups)




        
