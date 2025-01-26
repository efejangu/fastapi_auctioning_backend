from tokenize import group
from app.core.repo.bid.bidding_main import BiddingMain
from app.core.repo.auth.session_tokens import SessionTokens
from fastapi import WebSocket, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import User

from fastapi import WebSocket, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import User
from app.core.repo.bid.bidding_main import BiddingMain
from app.core.repo.auth.session_tokens import SessionTokens
from typing import Optional
import re
from fastapi.responses import JSONResponse


class BiddingService:
    def __init__(self, bidding_main: BiddingMain):
        self.bidding_main = bidding_main

    async def create_group(self, websocket: WebSocket, group_name: str, target_price: float):
        """
        Creates a new group with error handling and validation.
        """
        try:
            # Validate target price
            if target_price <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Target price must be greater than zero."
                )

            # Validate group name
            if re.match("[\d\W_]", group_name):
                # validator for ensuring group names with symbols and numbers cannot be used
                raise HTTPException(
                    status_code=400,
                    detail="Group name must only contain letters and underscores, no numbers or special characters."
                )
            # Create the group
            await self.bidding_main.create_group(websocket, group_name, target_price)
            return {"message": f"Group '{group_name}' created successfully."}

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating group: {str(e)}"
            )
    async def join_group(self, websocket: WebSocket, group_name: str):
        if re.match("[\d\W_]", group_name):
            #validator for ensuring group names with symbols and numbers cannot be used
            raise HTTPException(
                status_code=400,
                detail="Group name must only contain letters and underscores, no numbers or special characters."
            )
        await self.bidding_main.join_group(websocket, group_name)

    async def place_bid(self, websocket: WebSocket, bid: float, group_name: str, bidder_name: str):
        """
        Places a bid with error handling and validation.
        """
        try:
            # Validate bid amount
            if bid <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Bid must be greater than zero."
                )

            # Validate user

            # Place the bid
            print(websocket)
            await websocket.accept()
            data = await websocket.receive_json()
            await self.bidding_main.place_bid(
                websocket=websocket,
                bid=data["bid"],
                bidder_name=bidder_name,
                group_name=group_name
            )
            return JSONResponse(content={"message": "Bid placed successfully."})

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error placing bid: {str(e)}"
            )

    async def disconnect(self, websocket: WebSocket, group_name: str):
        """
        Disconnects a user from a group with error handling.
        """
        try:
            await self.bidding_main.disconnect(websocket, group_name)
            return {"message": "Disconnected successfully."}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error disconnecting user: {str(e)}"
            )

    async def close_auction(self, group_name: str):
        """
        Closes an auction with error handling.
        """
        try:
            await self.bidding_main.close_auction(group_name)
            return {"message": "Auction closed successfully."}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error closing auction: {str(e)}"
            )

    async def bidding_status(self, group_name: str):
        """
        Retrieves the bidding status with error handling.
        """
        try:
            status = await self.bidding_main.bidding_status(group_name)
            return {"status": status}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving bidding status: {str(e)}"
            )

    async def get_groups(self):
        """
        Retrieves all groups with error handling.
        """
        try:
            groups = await self.bidding_main.get_groups()
            return {"groups": groups}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving groups: {str(e)}"
            )