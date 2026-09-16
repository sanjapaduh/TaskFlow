from sqlite3 import IntegrityError
from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import session
from starlette import status

from .main import get_db
from models import User
from database import SessionLocal


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

db_dependency = Annotated[session, Depends(get_db)]

class Create_User_Request(BaseModel):
    username: str = Field(pattern=r".*\d{1}.*")
    email: EmailStr


class Access_Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/create_user")
def create_user(
        db: db_dependency,
        user: Create_User_Request):

    create_user_model = User(
        username=user.username,
        email=user.email
    )

    try:
        db.add(create_user_model)
        db.commit()
        return {"message" : "user successfully created"}
    except IntegrityError:
        # If the unique constraint fails, we must rollback the failed transaction
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered."
        )
