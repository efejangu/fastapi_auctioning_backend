from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import session, get_db
from app.models import User
from fastapi import status
from app.core.repo.auth.pwd_hash import PasswordHash
from app.core.repo.auth.session_tokens import SessionTokens,timedelta
from app.schema import CreateUser
from fastapi import HTTPException
from typing import Union


class AuthRepository:

  async def authentication_handler(self, db: Session, form_data: Depends(OAuth2PasswordRequestForm)):
       user = await self.authenticate_user(form_data.username, form_data.password, db)
       sesh = await SessionTokens().create_access_token({"id": user.id})
       if not user:
           raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                               detail="Incorrect username or password")
       print(sesh)

  async def regisration_handler(self, form_data: CreateUser, db: Session):
       does_usr_exist = await self.get_user(form_data.email, db)
       if does_usr_exist:
           raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                               detail="User already exists"
                               )
       if form_data.password != form_data.confirm_password:
           raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                               detail="Passwords do not match"
                               )
       new_usr = User(
           first_name=form_data.first_name,
           last_name=form_data.last_name,
           email=form_data.email,
           username=form_data.username,
           password=PasswordHash().hash_password(form_data.password)
       )
       #add and commit user into db
       db.add(new_usr)
       db.commit()
       db.refresh(new_usr)
       #return status code for user being created successfully
       return {"status": 201, "message": "User created successfully"}

  async def get_user(self, email: Union[str, None], db: Session):
   identifier_length = isinstance(email, str) and (len(email) > 0)
   existing_user = None

   match email:
       case None:
           return False
       case identifier_length:
           existing_user = db.query(User).filter(User.email == email).first()

   del identifier_length
   return existing_user
    #add session as a dependancy
  async def authenticate_user(self, username: str, password: str, db: Session):
       pwd = PasswordHash()
       user = await self.get_user(username, db)
       if not user:
           return False
       if not pwd.verify_password(password, user.password):
           return False
       return user