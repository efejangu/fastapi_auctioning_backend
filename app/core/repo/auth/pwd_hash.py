from passlib.context import CryptContext
import os
from dotenv import load_dotenv


load_dotenv()
class PasswordHash:
    SCHEME  = os.getenv("PWD_ALGORITHM")
    def __init__(self):
        self.password_context = CryptContext(schemes=[self.SCHEME], deprecated="auto")

    def hash_password(self, password) -> str:
        return self.password_context.hash(password)

    def verify_password(self, plain_password, hashed_password) -> bool:
        return self.password_context.verify(plain_password, hashed_password)
