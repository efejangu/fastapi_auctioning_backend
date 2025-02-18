# import what is required to create tables
from sqlalchemy import Column, Integer, String, ForeignKey, UUID, Boolean, Float
from uuid import uuid4
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    first_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255))
    username = Column(String(255))
    password = Column(String(255))

    # user_biding_history = relationship("BidingHistory", backref="users")
    # item = relationship("Items", backref="users")

class BidingHistory(Base):
    __tablename__ = "user_biding_history"
    bidID = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    item_name = Column(String(255))
    price = Column(Float)
    buyer = Column(String(255))

    vendor = relationship("User", backref="user_biding_history")




