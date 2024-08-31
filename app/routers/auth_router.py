from fastapi_utils.cbv import cbv
from fastapi import APIRouter, Depends
from ..core.services.auth_service import AuthService
from fastapi.security import OAuth2PasswordRequestForm
import app.schema as schema
from typing import Annotated
from sqlalchemy.orm import Session
from app.database import get_db

dependancy = Annotated[Session, Depends(get_db)]

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}}
)

@cbv(auth_router)
class AuthRouter:
    def __init__(self):
        self.auth_service = AuthService()

    @auth_router.post("/login", response_model=schema.Token)
    async def login(self, db: dependancy ,form_data: OAuth2PasswordRequestForm = Depends()):
        return await self.auth_service.auth_handler(form_data, db)

    @auth_router.post("/signup")
    async def signup(self, form_data: schema.CreateUser, db: dependancy):
        return await self.auth_service.registration_handler(form_data,db)