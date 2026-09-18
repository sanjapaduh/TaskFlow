from datetime import timedelta, datetime, timezone
from sqlite3 import IntegrityError
from typing import Annotated

import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import session
from starlette import status

from database import SessionLocal
# from main import get_db
from models import User

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[session, Depends(get_db)]
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oath2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    username: str = Field(pattern=r".*\d{1}.*")
    email: EmailStr
    password: str


class AccessToken(BaseModel):
    access_token: str
    token_type: str

def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user




def create_token_access(username: str,
                        user_id: int,
                        expires_delta: timedelta | None = None):
    encode = {"sub": username, "id": user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oath2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="User is not authorized")
        return {"username": username, "id": user_id}
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User is not authorized")


@router.post("/create_user")
def create_user(
        db: db_dependency,
        user: CreateUserRequest):
    create_user_model = User(
        username=user.username,
        email=user.email,
        hashed_password=bcrypt_context.hash(user.password)

    )
    db.add(create_user_model)
    db.commit()


@router.post("/create_user/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db :db_dependency):
    user = authenticate_user(
        form_data.username,
        form_data.password,
        db
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User is not authorized")
    token = create_token_access(
        user.username,
        user.id,
        timedelta(minutes=20)
    )
    return {'access_token': token, 'token_type': 'bearer'}




