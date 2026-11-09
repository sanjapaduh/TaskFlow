from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import Todo, Tags


class TodoRepository:
    async def list_for_user(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> list[Todo]:
        statement = select(Todo).where(Todo.user_id == user_id)
        result = await db.execute(statement)
        return list(result.scalars().all())

    async def get_max_task_number(self, db: AsyncSession, user_id: int) -> int:
        stmt_max = select(func.max(Todo.user_task_number)).where(Todo.user_id == user_id)
        max_number = await db.scalar(stmt_max)
        return max_number or 0

    async def get_tag(self, db: AsyncSession, tag_name: str, tag_color: str) -> Tags | None:
        stmt_tag = select(Tags).where(Tags.name == tag_name, Tags.color == tag_color)
        tag_obj = await db.scalar(stmt_tag)
        return tag_obj


    async def save_todo(self, db: AsyncSession, todo: Todo):
        db.add(todo)
        await db.commit()
        await db.refresh(todo)
    #
    # async def create_todo(
    #     self,
    #     db: AsyncSession,
    #     user_id: int,
    #     todo_request: dict,
    #     tag: dict
    # ):
    #     todo_create_model = Todo(
    #         user_task_number=next_number,
    #         name=todo_request.name,
    #         description=todo_request.description,
    #         done=todo_request.done,
    #         importance=todo_request.importance,
    #
    #         user_id=user_id
    #     )
    #     stmt_tag = (select(Tags).where(Tags.name == tag.name, Tags.color == tag.color))
    #     tag_obj = await db.scalar(stmt_tag)
    #     if tag_obj:
    #         todo_create_model.tags.append(tag_obj)
    #     else:
    #         new_tag = Tags(name=tag.name, color=tag.color)
    #         todo_create_model.tags.append(new_tag)
    #     db.add(todo_create_model)
    #     await db.commit()
    #     await db.refresh(todo_create_model)

