from datetime import timedelta
from typing import Annotated

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import session
from starlette import status
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from models import User
from routers.schemas import CreateUserRequest
from database import get_db
from routers.security import authenticate_user, create_token_access, bcrypt_context

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

db_dependency = Annotated[session, Depends(get_db)]



templates = Jinja2Templates(directory="templates")


@router.post("/login-page")
def render_login_page(
        request: Request,
        db: db_dependency,
        user: CreateUserRequest
):
    user_token = authenticate_user(
        user.username,
        user.password,
        db
    )
    # hashed_password = bcrypt_context.hash(user.password).verify()
    stml = db.query(User).filter(user.username == User.username).first()
    if stml is None or not bcrypt_context.verify(user.password, stml.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    # return {"logged in status": "success"}
    token = create_token_access(
        user_token.username,
        user_token.id,
        timedelta(minutes=90)
    )
    return {'access_token': token, 'token_type': 'bearer', "logged" : "success", "user_id" : user_token.id}




    # return templates.TemplateResponse(request, "login.html")


@router.post("/create_user")
def create_user(
        db: db_dependency,
        user: CreateUserRequest
):
    create_user_model = User(
        username=user.username,
        email=user.email,
        hashed_password=bcrypt_context.hash(user.password)

    )
    db.add(create_user_model)
    db.commit()
    return {"success" : True, "user" : user},templates.TemplateResponse("registration")


@router.post("/token")
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
        timedelta(minutes=90)
    )
    return {'access_token': token, 'token_type': 'bearer'}




