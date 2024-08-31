from fastapi import HTTPException, status
from datetime import datetime, timedelta
from jose import jwt
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from fastapi import Depends


class SessionTokens:
    def __init__(self):
        self.SECRET_KEY = "mysecretkey"
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
       #self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

    async def create_access_token(self, subject: dict, expires_delta: int = None) -> dict:
        if expires_delta is not None:
            expires_delta = datetime.utcnow() + expires_delta
        else:
            expires_delta = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"exp": expires_delta, "sub": str(subject["id"])}
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)

        return {
            "access_token": encoded_jwt,
            "token_type": "bearer"
        }

    async def get_current_user_id(self, token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="auth/login"))]):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=self.ALGORITHM)
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                )
        except:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        return user_id

