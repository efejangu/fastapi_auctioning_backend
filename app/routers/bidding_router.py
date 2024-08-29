from fastapi_utils import cbv
from fastapi import APIRouter, Depends
from app.database import get_db
from typing import Annotated
from sqlalchemy.orm import Session

dependancy = Annotated[Session, Depends(get_db)]

bidding_router = APIRouter(
    prefix="/bidding",
    tags=["bidding"],
    responses={404: {"description": "Not found"}}
)


class BiddingRouter:
    pass