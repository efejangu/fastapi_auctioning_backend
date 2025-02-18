from fastapi import HTTPException, status, WebSocket
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated, Optional, Tuple
from fastapi import Depends
import logging
from typing import Dict


class SessionTokens:
    def __init__(self):
        self.SECRET_KEY = "mysecretkey" #I am aware this is bad practice
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


    async def verify_ws_token(self, websocket: WebSocket) -> Dict[str, Optional[str | int]]:
        """
        Verify token from WebSocket query parameters.

        Args:
            websocket (WebSocket): The WebSocket connection containing the token.

        Returns:
            Dict[str, Optional[str | int]]: A dictionary containing:
                - user_id: The verified user ID or None if verification fails.
                - error_message: Description of the error if any.
                - close_code: WebSocket close code if applicable.
        """
        token = websocket.query_params.get("token")
        if not token:
            self.logger.info("No token provided in WebSocket connection")
            return {
                "user_id": None,
                "error_message": "No authentication token provided",
                "close_code": 4001
            }

        try:
            # Decode and verify the token
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            user_id: str = payload.get("sub")

            if user_id is None:
                self.logger.warning("Token payload missing user_id")
                return {
                    "user_id": None,
                    "error_message": "Invalid token format: missing user ID",
                    "close_code": 4001
                }

            self.logger.info(f"Successfully verified WebSocket token for user {user_id}")
            return {
                "user_id": user_id,
                "error_message": None,
                "close_code": None
            }

        except jwt.ExpiredSignatureError:
            self.logger.warning("Token signature has expired")
            return {
                "user_id": None,
                "error_message": "Token has expired",
                "close_code": 4002
            }

        except jwt.JWTError as e:
            self.logger.error(f"JWT verification failed: {str(e)}")
            return {
                "user_id": None,
                "error_message": f"Invalid token: {str(e)}",
                "close_code": 4001
            }

        except Exception as e:
            self.logger.error(f"Unexpected error verifying WebSocket token: {str(e)}")
            return {
                "user_id": None,
                "error_message": "Internal server error during authentication",
                "close_code": 4001
            }