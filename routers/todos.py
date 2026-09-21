from typing import Annotated

from starlette.requests import Request

from models import Todo
from .auth import get_current_user, create_token_access
from fastapi import Depends, APIRouter
from pydantic import BaseModel, Field
from sqlalchemy.orm import session

from database import SessionLocal

# from .main import get_db

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


# toDoList = [1, 2, 3, 5]


class Todo_request(BaseModel):
    name: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=25)
    done: bool
    importance: int = Field(
        ge=0,
        le=10
    )


@router.post("/addtodo")
async def create_ToDo(todo_request: Todo_request,
                      db: db_dependency,
                      current_user: Annotated[dict, Depends(get_current_user)]):
    user_id = current_user.get("id")
    todo_create_model = Todo(
        name=todo_request.name,
        description=todo_request.description,
        done=todo_request.done,
        importance=todo_request.importance,
        user_id = user_id
    )
    db.add(todo_create_model)
    db.commit()


# @router.post("/addtodo", status_code=status.HTTP_201_CREATED)
# async def create_todo(
#         db:db_dependency,
#         todo_request:Todo_request):
#
#     todo_model = Todo(**todo_request, owner_id=user.get('id'))
#     db.add(todo_model)

@router.get("/todos")
def all_todos():
    return {"message": "toDoList"}
