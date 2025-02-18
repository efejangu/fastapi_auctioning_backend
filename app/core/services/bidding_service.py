# from app.core.repo.bid.bidding_main import BiddingMain
# from app.core.repo.auth.session_tokens import SessionTokens
# from fastapi import WebSocket, HTTPException
# from app.database import get_db
# from app.models import BidingHistory
# from sqlalchemy.orm import Session
# from app.models import User
# from app.core.repo.bid.bidding_main import BiddingMain
# from app.core.repo.auth.session_tokens import SessionTokens
# from typing import Optional
# import re
# import uuid
# from asyncio import Lock
from app.core.repo.bid.bidding_main import BiddingMain
from fastapi import WebSocket, HTTPException
from app.models import BidingHistory
from sqlalchemy.orm import Session
import re
import uuid
from asyncio import Lock
from fastapi_pagination import Params, Page, paginate, set_page


class BiddingService:
    def __init__(self, bidding_main: BiddingMain):
        self.bidding_main = bidding_main
        self.lock = Lock()

    async def create_group(self, websocket: WebSocket, group_name: str, item: str, target_price: float):


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
            await self.bidding_main.create_group(websocket, group_name, item, target_price)

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

    async def place_bid(self, id: str, bid: float, name, group_name: str ):
        """
        Places a bid with error handling and validation.
        """

        try:

            await self.bidding_main.place_bid(id, bid, name, group_name)

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error placing bid: {str(e)}"
            )

    async def disconnect(self, websocket: WebSocket, group_name: str, id: str):
        """
        Disconnects a user from a group with error handling.
        """
        try:
            await self.bidding_main.disconnect(websocket, group_name, id)

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error disconnecting user: {str(e)}"
            )

    async def close_auction(self, user_id: str, id: str, group_name: str, db: Session):
        """
        Closes an auction with error handling.
        """
        async with self.lock:
            try:
                group = self.bidding_main.connection_manager.group_objects[group_name]
                owner = await self.bidding_main.connection_manager.get_admin_websocket(group_name, id)
                if group.stack.get_size() == 0:
                    await owner.send_text("Closing Auction")
                    await self.bidding_main.close_auction(id,group_name)

                if group.stack.get_size() > 0:
                    await owner.send_text("Closing Auction")
                    model = BidingHistory(
                        vendor_id=uuid.UUID(user_id),
                        item_name= group.item_name,
                        price=group.stack.peek()["bid"],
                        buyer=group.stack.peek()["bidder"],
                    )

                    db.add(model)
                    db.commit()
                    db.refresh(model)
                    owner.send_text("Auction Saved")
                    await self.bidding_main.close_auction(id, group_name)

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

    async def get_groups(self, page: int, size: int ):
        """
        Retrieves all groups with error handling.
        """
        try:
            params = Params(page=page, size=size)
            rooms = await self.bidding_main.get_groups()

            return paginate(rooms, params)

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error Retrieving Groups"
            )