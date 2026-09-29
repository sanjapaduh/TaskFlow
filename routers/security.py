from datetime import timedelta, datetime, timezone

import jwt

from models import User
from routers.auth import bcrypt_context, SECRET_KEY, ALGORITHM


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
