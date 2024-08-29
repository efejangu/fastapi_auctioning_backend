from fastapi_utils.cbv import cbv
from fastapi import APIRouter, Depends
import app.schema as schema
from app.database import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from app.core.repo.auth.session_tokens import SessionTokens
from app.core.services.item_service import ItemService
from fastapi_pagination import paginate
from fastapi_pagination.links import Page


#__________________________dependencies___________________________________
current_usr = Annotated[str, Depends(SessionTokens().get_current_user_id)]
db_dependancy = Annotated[Session, Depends(get_db)]
#__________________________________________________________________________

item_router = APIRouter(
    prefix="/item",
    tags=["item"],
    responses={404: {"description": "Not found"}}
)
@cbv(item_router)
class ItemRouter:

    def __init__(self):
        self.item_repo = ItemService()

    @item_router.post("/create_listing")
    def create_item(self, item: schema.Items, db: db_dependancy, usr_token: current_usr):
        return self.item_repo.create_item(item, db, usr_token)

    @item_router.get("/listing{id}")
    def get_item(self, db: db_dependancy, id):
        return self.item_repo.get_item(db, id)
