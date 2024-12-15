# import what is required to create tables
from sqlalchemy import Column, Integer, String, ForeignKey, UUID, Boolean
from uuid import uuid4
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    username = Column(String)
    password = Column(String)

    # user_biding_history = relationship("BidingHistory", backref="users")
    # item = relationship("Items", backref="users")

class BidingHistory(Base):
    __tablename__ = "user_biding_history"
    bidID = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    item_name = Column(String)
    price = Column(Integer)
    buyer = Column(String)

    vendor = relationship("User", backref="user_biding_history")


class Items(Base):
    __tablename__ = "item"
    ItemID = Column(Integer, primary_key=True, index=True)
    owner_id = Column(UUID(), ForeignKey("users.id"))
    item_name = Column(String)
    item_description = Column(String)
    price = Column(Integer())
    available = Column(Boolean, nullable=False)

    owner = relationship("User", backref="item")