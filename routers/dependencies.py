from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from sqlalchemy.orm import session
from starlette import status

from database import get_db
from routers.auth import SECRET_KEY, ALGORITHM, oauth2_bearer


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="User id or name is not authorized")
        return {"username": username, "id": user_id}
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User is not authorized user")

Get_current_user = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[session, Depends(get_db)]
