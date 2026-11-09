from sqlalchemy import select
from sqlalchemy import update


from sqlalchemy.orm import joinedload

# from starlette.templating import Jinja2Templates

from models import Todo, Tags
from fastapi import APIRouter, HTTPException

from repositories import todo_repository
from .dependencies import db_dependency, Get_current_user
from .schemas import Tag_request, Todo_request
from services.todo_service import TodoNotFoundError, todo_service

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)




@router.get("")
async def list_todos(
        db: db_dependency,
        current_user: Get_current_user
):
    user_id = current_user.get("id")
    try:
        todo_model = await todo_service.list_todos(db, user_id)
    except TodoNotFoundError:
        raise HTTPException(status_code=404, detail="Todo not found")

    return {"Your todos": todo_model}


@router.get("/me")
async def check_current_user(current_user: Get_current_user):
    # If the cookie is missing or invalid, the dependency will throw a 401 error.
    # If it works, it will return the user dictionary.
    return {"message": "Cookie authentication works!", "user_data": current_user}

@router.post("")
async def create_ToDo(todo_request: Todo_request,
                      tag: Tag_request,
                      db: db_dependency,
                      current_user: Get_current_user):
    user_id = current_user.get("id")
    max_number = await todo_repository.get_max_task_number(db, user_id)
    todo_create_model = await todo_service.create_todo(db, user_id, todo_request, tag)
    todo_create_model = await todo_repository.save_todo(db, todo_create_model)
    return {
        "status": "success", "todo": {todo_create_model}
    }


@router.get("/{item_id}")
async def todo_item(item_id: int,
                    db: db_dependency,
                    current_user: Get_current_user
                    ):
    user_id = current_user.get("id")
    stmt = (
        select(Todo)
        .options(joinedload(
            Todo.tags))  # N+1 problem (todo.tag is lazyload which is impossible in async def. we use eager load)
        .where(Todo.user_task_number == item_id, Todo.user_id == user_id)
    )
    todo_model = await db.scalar(stmt)
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    return {"todo": todo_model}


@router.put("/{item_id}")
async def change_todo(item_id: int,
                      todo_request: Todo_request,
                      tag: Tag_request,
                      db: db_dependency,
                      current_user: Get_current_user):
    user_id = current_user.get("id")
    stml = (select(Todo)
            .options(joinedload(Todo.tags))
            .where(Todo.user_task_number == item_id, Todo.user_id == user_id))

    todo_model = await db.scalar(stml)
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    try:
        todo_model.name = todo_request.name
        todo_model.description = todo_request.description
        todo_model.importance = todo_request.importance
        todo_model.done = todo_request.done

        stmt_tag = (select(Tags).where(Tags.name == tag.name, Tags.color == tag.color))
        tag_obj = await db.scalar(stmt_tag)
        if tag_obj:
            tag_already_exists = any(existing_tag.id == tag_obj.id for existing_tag in todo_model.tags)

            if not tag_already_exists:
                todo_model.tags.append(tag_obj)
        else:
            new_tag_object = Tags(name=tag.name, color=tag.color)
            todo_model.tags.append(new_tag_object)
        await db.commit()
        await db.refresh(todo_model)
        return {"updated todo": "success"}
    except Exception as e:
        print(f"error {e}")
        raise HTTPException(status_code=404, detail="already exist")


@router.delete("/{item_id}")
async def delete_todo(
        item_id: int,
        db: db_dependency,
        current_user: Get_current_user
):
    user_id = current_user.get("id")
    stml = (select(Todo)
            .options(joinedload(Todo.tags))
            .where(Todo.user_task_number == item_id, Todo.user_id == user_id))
    todo_model = await db.scalar(stml)
    if todo_model is None:
        raise HTTPException(status_code=404, detail="there are not todo with this number ")

    await db.delete(todo_model)
    update_stmt = (
        update(Todo)
        .where(Todo.user_id == user_id, Todo.user_task_number > item_id)
        .values(user_task_number=Todo.user_task_number - 1)
    )
    await db.execute(update_stmt)

    await db.commit()
    return {"deletion": "success"}

