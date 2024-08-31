from pydantic import BaseModel

class CreateUser(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str

class Items(BaseModel):
    item_name: str
    item_description: str
    price: int
    available: bool

class Token(BaseModel):
    access_token: str
    token_type: str