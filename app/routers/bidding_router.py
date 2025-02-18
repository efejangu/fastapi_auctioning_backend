from fastapi import(
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    HTTPException,
    status,
)
from app.database import get_db
from sqlalchemy.orm import Session
from app.core.services.bidding_service import BiddingService
from app.core.repo.auth.session_tokens import SessionTokens
from app.core.repo.bid.bidding_logic import ConnectionManager
from app.core.repo.bid.bidding_main import BiddingMain
import re
import uuid
import logging
import traceback

from app.core.repo.auth.session_tokens import SessionTokens


logger = logging.getLogger(__name__)
bidding_router = APIRouter(
    prefix="/bidding",
    tags=["bidding"],
    responses={404: {"description": "Not found"}}
)

conn_manager = ConnectionManager()
bidding_main = BiddingMain(conn_manager)
bidding_service = BiddingService(bidding_main)

@bidding_router.websocket("/ws/create_room")
async def admin_endpoint(websocket: WebSocket, db: Session=Depends(get_db) ):
    #token validation logic
    await websocket.accept()
    token = await SessionTokens().verify_ws_token(websocket)
    if token["user_id"] is None:
        await websocket.send_text(token["error_message"])
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
    websocket.state.user = token["user_id"]
    try:
        while True:
            data = await websocket.receive_json()
            print(data)
            action = data["action"]
            match action:
                case "create_group":
                    if not (
                        all(key in data and data[key] is not None for key in ["group_name", "target_price", "item"])
                        and isinstance(data["group_name"], str)
                        and re.fullmatch(r"^[A-Za-z\s]+$", data["group_name"])
                        and isinstance(data["target_price"], (int, float))
                        and isinstance(data["item"], str)
                    ):
                        raise WebSocketException(
                            code=status.WS_1008_POLICY_VIOLATION,
                            reason="Invalid group_name or target_price"
                        )
                    await bidding_service.create_group(
                        websocket,
                        data["group_name"],
                        data["item"],
                        data["target_price"]
                    )
                case "close_group":
                    if not (
                        all(key in data and data[key] is not None for key in ["group_name", "id"])
                        and isinstance(data["group_name"], str)
                        and re.fullmatch(r"^[A-Za-z\s]+$", data["group_name"])
                        and isinstance(data["id"], str)
                        and uuid.UUID(data["id"], version=4).hex == data["id"].replace('-', '')
                    ):
                        raise WebSocketException(
                            code=status.WS_1008_POLICY_VIOLATION,
                            reason="Invalid group_name or id"
                        )
                    await bidding_service.close_auction(
                        websocket.state.user,
                        data["id"],
                        data["group_name"],
                        db
                    )
    except WebSocketDisconnect:
        traceback.print_exc()
        logger.info("WebSocket connection closed.")
        #TO_DO: Write a function that gets rid of disconnected connections due to erroes
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_text(f"error: an error occured: disconnecting user")
        traceback.print_exc()
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

@bidding_router.websocket("/ws/bid_interface")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        token = await SessionTokens().verify_ws_token(websocket)
        if token["user_id"] is None:
            await websocket.send_text(token["error_message"])
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        websocket.state.user = token["user_id"]
        while True:
            data = await websocket.receive_json()
            action = data["action"]
            match action:
                case "join_group":
                    if not (
                        all(key in data and data[key] is not None for key in ["group_name"])
                        and isinstance(data["group_name"], str)
                    ):
                        raise WebSocketException(
                            code=status.WS_1008_POLICY_VIOLATION,
                            reason="Invalid group_name"
                        )
                    await bidding_service.join_group(
                        websocket,
                        data["group_name"]
                    )
                case "disconnect":
                    if not (
                        all(key in data and data[key] is not None for key in ["group_name", "id"])
                        and isinstance(data["group_name"], str)
                        and re.fullmatch(r"^[A-Za-z\s]+$", data["group_name"])
                        and isinstance(data["id"], str)
                        and re.fullmatch(r"^[0-9a-f]{8}-?[0-9a-f]{4}-?4[0-9a-f]{3}-?[89ab][0-9a-f]{3}-?[0-9a-f]{12}\Z", data["id"], re.I)
                    ):
                        raise WebSocketException(
                            code=status.WS_1008_POLICY_VIOLATION,
                            reason="Invalid group_name or id"
                        )
                    await bidding_service.disconnect(
                        websocket,
                        data["group_name"],
                        data["id"]
                    )
                case "place_bid":
                    if not (
                        all(key in data and data[key] is not None for key in ["bid", "bidder_name", "id", "group_name"])
                        and isinstance(data["bid"], float)
                        and isinstance(data["bidder_name"], str)
                        and re.fullmatch(r"^[A-Za-z\s]+$", data["bidder_name"])
                        and isinstance(data["id"], str)
                    ):
                        raise WebSocketException(
                            code=status.WS_1003_UNSUPPORTED_DATA,
                            reason=(
                                "Invalid data: 'bid' must be a float, and 'bidder_name' must be a string "
                                "with no numbers/symbols."
                            )
                        )
                    id = data["id"]
                    bid = data["bid"]
                    bidder_name = data["bidder_name"]
                    group_name = data["group_name"]
                    await bidding_service.place_bid(
                        id,
                        bid,
                        bidder_name,
                        group_name
                    )
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed.")
    except Exception as e:
        logger.error(f"Connection error error: {str(e)}")
        traceback.print_exc()
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

@bidding_router.get("/get_groups")
async def get_groups(page: int = 1, size: int = 5):
    return await bidding_service.get_groups(page, size)
