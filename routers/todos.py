from sqlalchemy import func, select
from sqlalchemy import update


from sqlalchemy.orm import joinedload

from starlette.templating import Jinja2Templates

from models import Todo, Tags
from fastapi import APIRouter, HTTPException

from .dependencies import db_dependency, Get_current_user
from .shemas import Todo_request, Tag_request

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)

template = Jinja2Templates(directory="templates")


@router.post("/addtodo")
async def create_ToDo(todo_request: Todo_request,
                      tag: Tag_request,
                      db: db_dependency,
                      current_user: Get_current_user):
    user_id = current_user.get("id")
    stmt_max = select(func.max(Todo.user_task_number)).where(Todo.user_id == user_id)
    max_number = await db.scalar(stmt_max)
    next_number = (max_number or 0) + 1
    todo_create_model = Todo(
        user_task_number=next_number,
        name=todo_request.name,
        description=todo_request.description,
        done=todo_request.done,
        importance=todo_request.importance,

        user_id=user_id
    )

    stmt_tag = (select(Tags).where(Tags.name == tag.name, Tags.color == tag.color))
    tag_obj = await db.scalar(stmt_tag)
    if tag_obj:
        todo_create_model.tags.append(stmt_tag)
    else:
        new_tag = Tags(name=tag.name, color=tag.color)
        todo_create_model.tags.append(new_tag)
    db.add(todo_create_model)
    await db.commit()
    await db.refresh(todo_create_model)
    return {
        "status": "success"

    }


@router.get("/get/{item_id}")
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


@router.put("/change/item_id{item_id}")
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
            todo_model.tags.append(tag_obj)
        else:
            new_tag_object = Tags(name=tag.name, color=tag.color)
            # await db.flush()
            todo_model.tags.append(new_tag_object)
        await db.commit()
        await db.refresh(todo_model)
        return {"updated todo": "success"}
    except:
        raise HTTPException(status_code=404, detail="already exist")


@router.delete("/delete/todo:{item_id}")
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
        return HTTPException(status_code=404, detail="there are not todo with this number ")

    await db.delete(todo_model)
    update_stmt = (
        update(Todo)
        .where(Todo.user_id == user_id, Todo.user_task_number > item_id)
        .values(user_task_number=Todo.user_task_number - 1)
    )
    await db.execute(update_stmt)

    await db.commit()
    return {"deletion": "success"}


@router.get("/todos")
async def all_todos(
        db: db_dependency,
        current_user: Get_current_user
):
    user_id = current_user.get("id")
    stml = select(Todo).where(Todo.user_id == user_id)
    todo_model = await db.execute(stml).scalars().all()
    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo not found")

    return {"Your todos": todo_model}
