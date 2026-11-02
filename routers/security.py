import os
from datetime import timedelta, datetime, timezone

import jwt
from fastapi import HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select
from starlette import status

from models import User

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def authenticate_user(username: str, password: str, db):
    stmt = select(User).filter(User.username == username)
    user= await db.scalar(stmt)
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


async def get_current_user(request: Request):
    token_beared = request.cookies.get("access_token")
    if not token_beared:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = token_beared.replace("Baerer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="User id or name is not authorized")
        return {"username": username, "id": user_id}
    except Exception as e:
        print(f"JWT DECODE ERROR: {e}") # Look at your PyCharm terminal to see the exact crash reason!
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authorized user"
        )