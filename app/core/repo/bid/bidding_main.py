"""
Main module for bidding operations in the bidding application.

This module serves as the entry point for core bidding functionality,
coordinating interactions between different components of the bidding system.
"""
from fastapi import WebSocket
from .bidding_logic import AuctionGroup
from .conn_manager import ConnectionManager

class BiddingMain:
    def __init__(self, connection_manager=None):
        self.connection_manager = connection_manager or ConnectionManager()

    async def create_group(self, websocket: WebSocket, group_name: str, target_price: float):
        if group_name in self.connection_manager.groups:
            return {"message": "Group name already exists, try a different name.",
                    "status": 400
            }
        
        self.connection_manager.groups[group_name] = set()
        new_group = AuctionGroup(group_name, self.connection_manager, target_price)
        self.connection_manager.groups[group_name].add({f"{group_name}_object":new_group}) 
        
    async def connect(self, websocket: WebSocket, group_name: str):
        await self.connection_manager.connect(websocket, group_name)
        
    async def disconnect(self, websocket: WebSocket, group_name: str):
        await self.connection_manager.disconnect(websocket, group_name)
        
    async def place_bid(self, websocket: WebSocket, bid: float, bidder_name: str, group_name: str):
        group_obj = f"{group_name}_object"
        get_group = self.connection_manager.groups[group_name][group_obj]
        await get_group.place_bid(websocket, bid, bidder_name)

    async def close_auction(self, group_name: str):
        group_obj = f"{group_name}_object"
        get_group = self.connection_manager.groups[group_name][group_obj]
        await get_group.close_auction()

    async def bidding_status(group_name: str):
        group_obj = f"{group_name}_object"
        get_group = self.connection_manager.groups[group_name][group_obj]
        return await get_group.stack.peek()
        
