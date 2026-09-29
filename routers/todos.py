from sqlalchemy import func, select

from starlette.templating import Jinja2Templates
from starlette.requests import Request

from models import Todo
from .dependencies import Get_current_user, db_dependency
from fastapi import APIRouter, HTTPException

from .shemas import Todo_request

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)

template = Jinja2Templates(directory="templates")


@router.post("/addtodo")
async def create_ToDo(todo_request: Todo_request,
                      request: Request,
                      db: db_dependency,
                      current_user: Get_current_user):
    user_id = current_user.get("id")
    stmt = select(func.max(Todo.user_task_number)).where(Todo.user_id == user_id)
    max_number = db.scalar(stmt)
    next_number = (max_number or 0) + 1
    todo_create_model = Todo(
        user_task_number=next_number,
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
              current_user: Get_current_user
              ):
    user_id = current_user.get("id")
    stmt = select(Todo).where(Todo.user_task_number == item_id, Todo.user_id == user_id)

    todo_model = db.scalar(stmt)
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    return {"todo": todo_model}


@router.put("/change/item_id{item_id}")
async def change_todo(item_id: int,
                      todo_request: Todo_request,
                      db: db_dependency,
                      current_user: Get_current_user):
    user_id = current_user.get("id")
    stml = select(Todo).where(Todo.user_task_number == item_id, Todo.user_id == user_id)
    todo_model = db.scalar(stml)
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_model.name = todo_request.name
    todo_model.description = todo_request.description
    todo_model.importance = todo_request.importance
    todo_model.done = todo_request.done
    db.commit()
    db.refresh(todo_model)
    return {"updated todo": todo_model}


@router.delete("/delete/todo:{item_id}")
def delete_todo(
        item_id: int,
        db: db_dependency,
        current_user: Get_current_user
):
    user_id = current_user.get("id")
    stml = select(Todo).where(Todo.user_task_number == item_id, Todo.user_id == user_id)
    todo_model = db.scalar(stml)

    if todo_model is None:
        return HTTPException(status_code=404, detail="there are not todo with this number ")

    db.delete(todo_model)
    db.query(Todo).filter(Todo.user_id == user_id, Todo.user_task_number > item_id).update(
        {Todo.user_task_number: Todo.user_task_number - 1},
        synchronize_session=False)
    db.commit()
    return {"deletion": "success"}


@router.get("/todos")
def all_todos():
    return {"message": "toDoList"}
