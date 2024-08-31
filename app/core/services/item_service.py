from sqlalchemy.orm import Session
import app.schema as schema
from fastapi import Depends
from app.core.repo.auth.session_tokens import SessionTokens
from typing import Annotated
from app.core.repo.item.item_repository import ItemRepo

current_usr = Annotated[str, Depends(SessionTokens().get_current_user_id)]

class ItemService:

    def __init__(self):
        self.item_repo = ItemRepo()

    def create_item(self, item: schema.Items, db: Session, usr_token: current_usr):
        return self.item_repo.create_item(item, db, usr_token)


    def get_item(self, db: Session, id):
        return self.item_repo.get_item(db, id)