from fastapi import APIRouter, Depends, WebSocket, HTTPException, status
from app.database import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from app.core.services.bidding_service import BiddingService
from app.core.repo.auth.session_tokens import SessionTokens
from app.core.repo.bid.bidding_main import BiddingMain

bidding_router = APIRouter(
    prefix="/bidding",
    tags=["bidding"],
    responses={404: {"description": "Not found"}}
)

@bidding_router.websocket("/ws/create_group")
async def create_group(
    websocket: WebSocket,
    group_name: str,
    target_price: float,
    db: Session = Depends(get_db)
):
    # Accept the connection first
    await websocket.accept()
    
    # Then verify the token
    session_tokens = SessionTokens()
    user_id, error_message, close_code = await session_tokens.verify_ws_token(websocket)
    
    if user_id is None:
        await websocket.close(code=close_code, reason=error_message)
        return
    
    bidding_service = BiddingService(db=db, bidding_main=BiddingMain())
    await bidding_service.create_group(websocket, group_name, target_price)

@bidding_router.websocket("/ws/connect")
async def connect(
    websocket: WebSocket,
    group_name: str,
    db: Session = Depends(get_db)
):
    # Accept the connection first
    await websocket.accept()
    
    # Then verify the token
    session_tokens = SessionTokens()
    user_id, error_message, close_code = await session_tokens.verify_ws_token(websocket)
    
    if user_id is None:
        await websocket.close(code=close_code, reason=error_message)
        return
    
    bidding_service = BiddingService(db=db, bidding_main=BiddingMain())
    await bidding_service.connect(websocket, group_name)

@bidding_router.websocket("/ws/disconnect")
async def disconnect(
    websocket: WebSocket,
    group_name: str,
    db: Session = Depends(get_db)
):
    # Accept the connection first
    await websocket.accept()
    
    # Then verify the token
    session_tokens = SessionTokens()
    user_id, error_message, close_code = await session_tokens.verify_ws_token(websocket)
    
    if user_id is None:
        await websocket.close(code=close_code, reason=error_message)
        return
    
    bidding_service = BiddingService(db=db, bidding_main=BiddingMain())
    await bidding_service.disconnect(websocket, group_name)

@bidding_router.websocket("/ws/place_bid")
async def place_bid(
    websocket: WebSocket,
    bid: float,
    group_name: str,
    db: Session = Depends(get_db)
):
    # Accept the connection first
    await websocket.accept()
    
    # Then verify the token
    session_tokens = SessionTokens()
    user_id, error_message, close_code = await session_tokens.verify_ws_token(websocket)
    
    if user_id is None:
        await websocket.close(code=close_code, reason=error_message)
        return
    
    bidding_service = BiddingService(db=db, bidding_main=BiddingMain())
    await bidding_service.place_bid(websocket, bid, group_name, user_id)
    await bidding_service.bidding_status(group_name)

@bidding_router.get("/get_groups")
async def get_groups(
    user_id: Annotated[str, Depends(SessionTokens().get_current_user_id)],
    db: Session = Depends(get_db)
):
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    bidding_service = BiddingService(db=db, bidding_main=BiddingMain())
    return await bidding_service.get_groups()