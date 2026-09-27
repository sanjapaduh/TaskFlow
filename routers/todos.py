from typing import Annotated

from sqlalchemy import Select, func, select

from starlette.templating import Jinja2Templates
from starlette.requests import Request

from models import Todo
from .auth import get_current_user
from fastapi import Depends, APIRouter, HTTPException
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
template = Jinja2Templates(directory="templates")


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
                      request: Request,
                      db: db_dependency,
                      current_user: Annotated[dict, Depends(get_current_user)]):
    user_id = current_user.get("id")
    stmt = select(func.max(Todo.user_task_number)).where(Todo.user_id == user_id)
    max_number = db.scalar(stmt)
    next_number = (max_number or 0) + 1
    todo_create_model = Todo(
        user_task_number = next_number,
        name=todo_request.name,
        description=todo_request.description,
        done=todo_request.done,
        importance=todo_request.importance,
        user_id=user_id
    )
    db.add(todo_create_model)
    db.commit()
    return template.TemplateResponse(request, "add-todo.html")


@router.get("/get/{item_id}")
def todo_item(item_id: int,
              db: db_dependency,
              current_user: Annotated[dict, Depends(get_current_user)]
              ):
    user_id = current_user.get("id")
    stmt = select(Todo).where(Todo.user_task_number == item_id, Todo.user_id == user_id)

    todo_model = db.scalar(stmt)
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    return {"todo": todo_model}

@router.put("/todo/change/item_id{item_id}")
async def change_todo(item_id:int,
                      todo_request: Todo_request,
                      db: db_dependency,
                      current_user: Annotated[dict, Depends(get_current_user)]):
    user_id = current_user.get("id")
    stml = select(Todo).where(Todo.user_task_number == item_id, Todo.user_id == user_id)
    todo_model= db.scalar(stml)
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_model.name = todo_request.name
    todo_model.description = todo_request.description
    todo_model.importance = todo_request.importance
    todo_model.done = todo_request.done
    db.commit()
    db.refresh(todo_model)
    return {"updated todo" : todo_model}

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
