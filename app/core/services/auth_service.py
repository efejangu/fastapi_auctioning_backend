from app.core.repo.auth.auth_repository import AuthRepository
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
import app.schema as schema
from sqlalchemy.orm import Session
from app.database import get_db


class AuthService:
    def __init__(self):
        self.auth_repo = AuthRepository()

    # create four empty methods named auth_handler, registration_handler, get_access_token, logout

    def auth_handler(self, db: Session ,form_data: OAuth2PasswordRequestForm = Depends()):
        return self.auth_repo.authentication_handler(db, form_data)

    def registration_handler(self, form_data: schema.CreateUser, db: Session):
        return self.auth_repo.registration_handler(form_data, db)

    def get_access_token(self):
        pass

    def logout(self):
        pass