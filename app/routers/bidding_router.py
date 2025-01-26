from fastapi import APIRouter, Depends, WebSocket, HTTPException, status
from app.database import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from app.core.services.bidding_service import BiddingService
from app.core.repo.auth.session_tokens import SessionTokens
from app.core.repo.bid.bidding_logic import ConnectionManager
from app.core.repo.bid.bidding_main import BiddingMain
from fastapi import WebSocket, WebSocketException
from app.core.repo.auth.session_tokens import SessionTokens
from app.core.services.bidding_service import BiddingService
import re

bidding_router = APIRouter(
    prefix="/bidding",
    tags=["bidding"],
    responses={404: {"description": "Not found"}}
)

conn_manager = ConnectionManager()
bidding_main = BiddingMain(conn_manager)
bidding_service = BiddingService(bidding_main)

def starts_with_number(s):
    # Regular expression to check if a string starts with a number
    pattern = r"^\d"
    return bool(re.match(pattern, s))


@bidding_router.websocket("/ws/connect")
async def connect(websocket:WebSocket, session: Annotated[Session, Depends(get_db)], group_name: str, target_price: float):
    if starts_with_number(group_name):
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                detail="Group name must not start with a number"
            )
    await bidding_service.create_group(websocket, group_name, target_price)


@bidding_router.websocket("/ws/join_group")
async def join_group(websocket:WebSocket, group_name: str):
    await bidding_service.join_group(websocket, group_name)



@bidding_router.get("/bidding/get_groups")
async def get_groups():
    return await bidding_main.get_groups()


