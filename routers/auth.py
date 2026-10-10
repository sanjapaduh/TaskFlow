from datetime import timedelta
from typing import Annotated

from fastapi.security import  OAuth2PasswordRequestForm

from fastapi import Depends, APIRouter, HTTPException
from starlette import status
from starlette.templating import Jinja2Templates

from models import User
from routers.dependencies import db_dependency
from routers.schemas import CreateUserRequest
from routers.security import authenticate_user, create_token_access, bcrypt_context

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)






@router.post("/login-page")
async def render_login_page(
        db: db_dependency,
        user: CreateUserRequest
):
    user_token = await authenticate_user(
        user.username,
        user.password,
        db
    )
    if not user_token :
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    token = create_token_access(
        user_token.username,
        user_token.id,
        timedelta(minutes=90)
    )
    return {'access_token': token, 'token_type': 'bearer', "logged" : user}






@router.post("/create_user")
async def create_user(
        db: db_dependency,
        user: CreateUserRequest
):
    create_user_model = User(
        username=user.username,
        email=user.email,
        hashed_password=bcrypt_context.hash(user.password)

    )
    db.add(create_user_model)
    await db.commit()
    return {"success" : True}

#
@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db :db_dependency):
    user = await authenticate_user(
        form_data.username,
        form_data.password,
        db
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User is not authorized")
    token =  create_token_access(
        user.username,
        user.id,
        timedelta(minutes=90)
    )
    return {'access_token': token, 'token_type': 'bearer'}




