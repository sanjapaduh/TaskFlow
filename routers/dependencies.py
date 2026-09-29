from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import session

from database import get_db
from routers.security import get_current_user

Get_current_user = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[session, Depends(get_db)]
