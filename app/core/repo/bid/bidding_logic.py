import asyncio
from hmac import new
from typing import Optional
from fastapi import WebSocket
from app.core.repo.bid.conn_manager import ConnectionManager
from app.core.repo.bid.bidding_stack import Stack

class AuctionGroup:
    def __init__(self, group_name: str, item_name: str, connection_manager: ConnectionManager, target_price: float):
        self.group_name = group_name
        self.item_name = item_name
        self.connection_manager = connection_manager
        self.highest_bid: Optional[float] = None
        self.highest_bidder: Optional[str] = None
        self.auction_open = True
        self.prev_value = None
        self.target_price = target_price
        self.stack = Stack()# Stack to store bids

    async def place_bid(self, websocket: WebSocket, bid: float, bidder_name: str):
        if not self.auction_open:
            await websocket.send_text("Auction is closed. No more bids can be placed.")
            return

        # Validate bid amount
        if bid <= 0:
            await websocket.send_text("Bid must be greater than zero.")
            return
            
        # Validate minimum increment (e.g., 1% of current highest bid)
        min_increment = self.highest_bid * 0.01 if self.highest_bid else 0
        if self.highest_bid and bid < (self.highest_bid + min_increment):
            await self.connection_manager.broadcast(self.group_name, f"Bid must be at least {self.highest_bid + min_increment:.2f}")
            return

        if self.highest_bid is None or bid > self.highest_bid:
            self.highest_bid = bid
            self.highest_bidder = bidder_name
            await self.connection_manager.broadcast(self.group_name, f"New highest bid: {bid} by {bidder_name}")
            self.stack.push({'bid': bid, 'bidder': bidder_name})
            self.prev_value = bid
            self.target_price = self.highest_bid + (self.target_price * 0.01)
            await self.connection_manager.broadcast(self.group_name,f" Auction price is now set at ${bid}")
        else:
            await websocket.send_text(f"Bid too low. Current highest bid is {self.highest_bid} by {self.highest_bidder}.")

    async def check_target_price(self):
        if self.highest_bid and self.highest_bid > self.target_price:
            await self.close_auction()

    async def close_auction(self):
        #TO-DO: store data of the winner of the bid
        self.auction_open = False
        self.stack.collapse()
        await self.cleanup()

    async def cleanup(self):
        """Method to properly cleanup resources"""
        await self.connection_manager.broadcast(self.group_name, "Auction Closed")
        self.connection_manager.group_admins.pop(self.group_name)
        self.connection_manager.group_members.pop(self.group_name)
        self.connection_manager.group_objects.pop(self.group_name)
            
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
