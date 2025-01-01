from tokenize import group
from app.core.repo.bid.bidding_main import BiddingMain
from app.core.repo.auth.session_tokens import SessionTokens
from fastapi import WebSocket, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import User




class BiddingService:
    def __init__(self, db: Session, bidding_main: BiddingMain):
        self.db = db
        self.bidding_main = bidding_main

    
    async def create_group(self, websocket: WebSocket, group_name: str, target_price: float):
        await self.bidding_main.create_group(websocket, group_name, target_price)

    async def connect(self, websocket: WebSocket, group_name: str):
        await self.bidding_main.connect(websocket, group_name)

    async def place_bid(self, websocket: WebSocket, bid: float, group_name: str, user_id: str):
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
                
            await self.bidding_main.place_bid(
                websocket, 
                bid, 
                bidder_name=str(user.first_name),
                group_name=group_name
            )
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error placing bid: {str(e)}"
            )

    async def disconnect(self, websocket: WebSocket, group_name: str):
        await self.bidding_main.disconnect(websocket, group_name)

    async def close_auction(self, group_name: str):
        await self.bidding_main.close_auction(group_name)
    
    async def bidding_status(self, group_name: str):
        await self.bidding_main.bidding_status(group_name)
        
    async def get_groups(self):
        return await self.bidding_main.get_groups()