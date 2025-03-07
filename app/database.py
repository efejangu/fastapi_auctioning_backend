# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker,query, Session
# from sqlalchemy.ext.declarative import declarative_base
# import pymysql

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()
# mariad/ mysql db code
SQLALCHEMY_DATABASE_URL = os.getenv('DB_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False,autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close
#______________________________uncomment to use sqlite ________________________________
# use this to test functionality of the database with sqlite
#
# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# # SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
# 3306
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
#

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
