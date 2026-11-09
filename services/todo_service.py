from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from models import Todo, Tags
from repositories.todo_repository import TodoRepository


class TodoNotFoundError(Exception):
    """Raised when a user has no matching todos."""


class TodoService:
    def __init__(self, repository: TodoRepository):
        self.repository = repository

    async def list_todos(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> list[Todo]:
        todos = await self.repository.list_for_user(db, user_id)
        if not todos:
            raise TodoNotFoundError
        return todos

    async def next_task_number(
            self,
            max_number: int
    ) -> int:
        next_number = (max_number or 0) + 1
        return next_number

    async def create_todo(
            self,
            db: AsyncSession,
            user_id: int,
            todo_request: dict,
            tag: dict):
        next_number = await self.repository.get_max_task_number(db, user_id) + 1
        todo_create_model = Todo(
            user_task_number=next_number,
            name=todo_request.name,
            description=todo_request.description,
            done=todo_request.done,
            importance=todo_request.importance,
            user_id=user_id
        )
        tag_obj = await self.repository.get_tag(db, tag.name, tag.color)

        if tag_obj:
            todo_create_model.tags.append(tag_obj)
        else:
            new_tag = Tags(name=tag.name, color=tag.color)
            todo_create_model.tags.append(new_tag)




todo_service = TodoService(TodoRepository())
