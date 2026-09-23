from string import Template
from typing import Annotated

from sqlalchemy.engine import url
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from starlette.requests import Request

from models import Todo
from .auth import get_current_user
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
template= Jinja2Templates(directory="templates")

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
                      request:Request,
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
    return template.TemplateResponse(request, "add-todo.html")


@router.get("/get/{item_id}")
def todo_item(item_id: str,
              db : db_dependency,
              current_user: Annotated[dict, Depends(get_current_user)]
              ):
    try:
        user_id = current_user.get("id")
        todo_id_request = db.query(Todo).filter(Todo.id == item_id, Todo.user_id== user_id).first()

        return {"todo" : todo_id_request}



    except:
            return {"error"}






@router.put("/todo/change")
async def change_todo(todo_request: Todo_request,
                      request:Request,
                      db:db_dependency,
                      current_user:Annotated[dict, Depends(get_current_user)]):
    user_id = current_user.get("id")
    todo_changed_model = Todo(
        name=todo_request.name,
        description=todo_request.description,
        done=todo_request.done,
        importance=todo_request.importance
    )
    db.commit(todo_request)

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
