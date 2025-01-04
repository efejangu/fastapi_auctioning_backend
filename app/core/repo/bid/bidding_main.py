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

class BiddingMain:
    def __init__(self, connection_manager=None):
        self.connection_manager = connection_manager or ConnectionManager()

    async def create_group(self, websocket: WebSocket, group_name: str, target_price: float):
        if group_name in self.connection_manager.groups:
            return {"message": "Group name already exists, try a different name.",
                    "status": 400
            }
        
        self.connection_manager.groups[group_name] = {}
        new_group = AuctionGroup(group_name, self.connection_manager, target_price)
        self.connection_manager.groups[group_name][f"{group_name}_object"] = new_group
        self.connection_manager.groups[group_name]["connections"] = set()
        
    async def connect(self, websocket: WebSocket, group_name: str):
        await self.connection_manager.connect(websocket, group_name)
        
    async def disconnect(self, websocket: WebSocket, group_name: str):
        await self.connection_manager.disconnect(websocket, group_name)
        
    async def place_bid(self, websocket: WebSocket, bid: float, bidder_name: str, group_name: str):
        if group_name not in self.connection_manager.groups:
            raise HTTPException(status_code=404, detail="Group not found")
        if bid <= 0:
            raise HTTPException(status_code=400, detail="Bid must be greater than zero")
        
        group_obj = f"{group_name}_object"
        get_group = self.connection_manager.groups[group_name][group_obj]
        await get_group.place_bid(websocket, bid, bidder_name)

    async def close_auction(self, group_name: str):
        group_obj = f"{group_name}_object"
        get_group = self.connection_manager.groups[group_name][group_obj]
        #fix 45
        await get_group.close_auction()

    async def bidding_status(self, group_name: str):
         group_obj = self.connection_manager.groups[group_name][f"{group_name}_object"]
         return group_obj.stack.peek()

    async def get_groups(self):
        group = {}
        if len(self.connection_manager.groups) == 0:
            return {"details": "No groups available"}
     
        for key, value in self.connection_manager.groups.items():
            group["group_name"] = key
            group["status"] = value["status"]["group_name_object"].status
            group ["count"] = await self.connection_manager.get_group_count(key)
            group["target_price"] = value["group_name_object"].target_price
        
        return group




        
