from tokenize import group
from app.core.repo.bid.bidding_main import BiddingMain
from app.core.repo.auth.session_tokens import SessionTokens
from fastapi import WebSocket
from fastapi import Depends
from sqlalchemy.orm import Session
from app.models import User




token = SessionTokens()
class BiddingService:
    def __init__(self):
        self.bidding_main = BiddingMain()

    
    async def create_group(self, websocket: WebSocket, group_name: str, target_price: float):
        await self.bidding_main.create_group(websocket, group_name, target_price)

    async def connect(self, websocket: WebSocket, group_name: str):
        await self.bidding_main.connect(websocket, group_name)

    async def place_bid(self, websocket: WebSocket, bid: float, group_name: str, user_id: str):
        user_name = Session()
        user_name =user_name.query(User).filter(User.id == user_id).first().first_name
        await self.bidding_main.place_bid(websocket, bid, bidder_name=user_name, group_name=group_name)

    async def disconnect(self, websocket: WebSocket, group_name: str):
        await self.bidding_main.disconnect(websocket, group_name)

    async def close_auction(self, group_name: str):
        await self.bidding_main.close_auction(group_name)
    
    async def bidding_status(self, group_name: str):
        await self.bidding_main.bidding_status(group_name)
        