from fastapi import FastAPI
from uvicorn import run
from app.models import User, Base
from app.database import get_db, engine
from app.routers.auth_router import auth_router
from app.routers.items_router import item_router
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_pagination(app)
app.include_router(auth_router)
app.include_router(item_router)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    run(app, host="127.0.0.1", port=8000)