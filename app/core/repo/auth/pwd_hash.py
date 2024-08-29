from passlib.context import CryptContext

# I am aware sensitive info like this is meant to be stored in an env file bare with me pls

class PasswordHash:
    def __init__(self):
        self.password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password) -> str:
        return self.password_context.hash(password)

    def verify_password(self, plain_password, hashed_password) -> bool:
        return self.password_context.verify(plain_password, hashed_password)
