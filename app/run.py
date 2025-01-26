from fastapi import FastAPI
from uvicorn import run
from app.models import User, Base
from app.database import get_db, engine

from app.routers.auth_router import auth_router
from app.routers.items_router import item_router
from app.routers.bidding_router import bidding_router

from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from datetime import datetime


# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # File handler - logs everything to a file
        logging.FileHandler(
            f'logs/app_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        ),
        # Console handler - logs everything to console
        logging.StreamHandler()
    ]
)

# Create logger
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
# ⚠️ SECURITY WARNING: DO NOT USE THESE SETTINGS IN PRODUCTION! ⚠️
# These settings allow any localhost connection for development.
# For production, specify exact origins and remove wildcards.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_pagination(app)
app.include_router(auth_router)
app.include_router(item_router)
app.include_router(bidding_router)

if __name__ == "__main__":
    logger.info("Starting FastAPI application")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    run(
        app,
        host="127.0.0.1",
        port=8000,
        ws_ping_interval=20.0,
        ws_ping_timeout=20.0,
    )