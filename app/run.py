from fastapi import FastAPI, Depends
from uvicorn import run
from sqlalchemy.orm import Session
from app.models import User, Base
from app.database import get_db, engine
from app.schema import CreateUser
from app.routers.auth_router import auth_router
from app.routers.items_router import item_router
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#add_pagination(app)

app.include_router(auth_router)
app.include_router(item_router)
run(app, host="127.0.0.1", port=8000)


Base.metadata.create_all(bind=engine)