from fastapi import HTTPException, status, WebSocket
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated, Optional, Tuple
from fastapi import Depends
import logging

class SessionTokens:
    def __init__(self):
        self.SECRET_KEY = "mysecretkey"
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self.logger = logging.getLogger(__name__)

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
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        return user_id

    async def verify_ws_token(self, websocket: WebSocket) -> Tuple[Optional[str], Optional[str], Optional[int]]:
        """
        Verify token from WebSocket query parameters
        Returns:
            Tuple[Optional[str], Optional[str], Optional[int]]: 
            - user_id: The verified user ID or None if verification fails
            - error_message: Description of the error if any
            - close_code: WebSocket close code if applicable
        """
        token = websocket.query_params.get("token")
        if not token:
            self.logger.warning("No token provided in WebSocket connection")
            return None, "No authentication token provided", 4001

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            user_id: str = payload.get("sub")
            
            if user_id is None:
                self.logger.warning("Token payload missing user_id")
                return None, "Invalid token format: missing user ID", 4001

            # Check token expiration
            exp = payload.get("exp")
            if exp is None:
                self.logger.warning("Token missing expiration")
                return None, "Invalid token format: missing expiration", 4001
            
            if datetime.fromtimestamp(exp) < datetime.utcnow():
                self.logger.warning(f"Expired token for user {user_id}")
                return None, "Token has expired", 4002

            self.logger.info(f"Successfully verified WebSocket token for user {user_id}")
            return user_id, None, None

        except jwt.ExpiredSignatureError:
            self.logger.warning("Token signature has expired")
            return None, "Token has expired", 4002
            
        except jwt.JWTError as e:
            self.logger.error(f"JWT verification failed: {str(e)}")
            return None, f"Invalid token: {str(e)}", 4001
            
        except Exception as e:
            self.logger.error(f"Unexpected error verifying WebSocket token: {str(e)}")
            return None, "Internal server error during authentication", 4001
