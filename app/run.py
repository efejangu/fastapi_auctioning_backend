# from fastapi import FastAPI
# from uvicorn import run
# from app.models import User, Base
# from app.database import get_db, engine
#
# from app.routers.auth_router import auth_router
# from app.routers.bidding_router import bidding_router
#
# from fastapi_pagination import add_pagination
# from fastapi_pagination.utils import disable_installed_extensions_check
# from fastapi.middleware.cors import CORSMiddleware
# import logging
# import os
# from datetime import datetime
#
#
# # Create logs directory if it doesn't exist
# os.makedirs("../logs", exist_ok=True)
#
# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         # File handler - logs everything to a file
#         logging.FileHandler(
#             f'../logs/app_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
#         ),
#         # Console handler - logs everything to console
#         logging.StreamHandler()
#     ]
# )
#
# # Create logger
# logger = logging.getLogger(__name__)
#
# Base.metadata.create_all(bind=engine)
# app = FastAPI()
#
# # Configure CORS
# # ⚠️ SECURITY WARNING: DO NOT USE THESE SETTINGS IN PRODUCTION! ⚠️
# # These settings allow any localhost connection for development.
# # For production, specify exact origins and remove wildcards.
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[""],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# add_pagination(app)
# disable_installed_extensions_check()
#
# app.include_router(auth_router)
# app.include_router(bidding_router)
#
# if __name__ == "__main__":
#     logger.info("Starting FastAPI application")
#     # Base.metadata.create_all(bind=engine)
#     logger.info("Database tables created")
#     run(
#         app,
#         host="0.0.0.0",
#         port=8000,
#         ws_ping_interval=20.0,
#         ws_ping_timeout=20.0,
#     )


from fastapi import FastAPI
from uvicorn import run
from app.models import User, Base
from app.database import get_db, engine

from app.routers.auth_router import auth_router
from app.routers.bidding_router import bidding_router

from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check
from fastapi.middleware.cors import CORSMiddleware
import logging
import graypy
import os
from datetime import datetime


#Create logs directory if it doesn't exist
log_dir = os.path.abspath("../logs")
os.makedirs(log_dir, exist_ok=True)

#set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# File logging
file_handler = logging.FileHandler(
    os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Console logging
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Graylog logging
host = os.environ.get("GRAY_HOST")
port = os.environ.get("GRAY_PORT")
if graylog_host and graylog_port:
    try:
        graylog_handler = graypy.GELFUDPHandler(graylog_host, int(graylog_port))
        logger.addHandler(graylog_handler)
        logger.info("Graylog handler successfully added.")
    except Exception as e:
        logger.error(f"Failed to set up Graylog handler: {e}")


# Create logger
logger.addHandler(handler)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.get("/")
def home():
    return {"message":"welcome! /n bidding app is now running"}


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
disable_installed_extensions_check()

app.include_router(auth_router)
app.include_router(bidding_router)


if __name__ == "__main__":
    logger.info("Starting FastAPI application")
    # Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    run(
        app,
        host="0.0.0.0",
        port=8000,
        ws_ping_interval=20.0,
        ws_ping_timeout=20.0,
    )