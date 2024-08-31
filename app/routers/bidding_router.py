from fastapi_utils import cbv
from fastapi import APIRouter, Depends
from app.database import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi_utils.cbv import cbv

dependancy = Annotated[Session, Depends(get_db)]

bidding_router = APIRouter(
    prefix="/bidding",
    tags=["bidding"],
    responses={404: {"description": "Not found"}}
)

@cbv(bidding_router)
class BiddingRouter:
    # create 4 methods within this class their names are create_bid, enter_bid, place_bid and exit_room. Make all aof these methods blank with no meaning no parameters or arguments and put a pass statement in all of them
    def create_bid(self):
        pass
    def enter_bid(self):
        pass
    def place_bid(self):
        pass
    def exit_room(self):
        pass

