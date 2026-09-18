from typing import Annotated

from fastapi import Depends, APIRouter
from pydantic import BaseModel, Field
from sqlalchemy.orm import session
from starlette import status

from database import SessionLocal
# from .main import get_db
from models import Todo

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[session, Depends(get_db)]
toDoList = [1, 2, 3, 5]


class Todo_request(BaseModel):
    name : str = Field(min_length=3)
    description : str = Field(min_length=3, max_length=25)
    done : bool
    importance : int = Field(
        ge = 0,
        le = 10
    )
# Query - for filter the url
# Field - for filter in json

# @app.post("/addtodo")
# def create_ToDo(todo : Todo_request):
#     toDoList.append(todo)
#     return{"message" : todo}


# @router.post("/addtodo", status_code=status.HTTP_201_CREATED)
# async def create_todo(
#         db:db_dependency,
#         todo_request:Todo_request):
#
#     todo_model = Todo(**todo_request, owner_id=user.get('id'))
#     db.add(todo_model)

@router.get("/todos")
def all_todos():
    return {"message" : toDoList}
