from typing import List

from sqlalchemy.orm import relationship, Mapped, mapped_column

from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class User(Base):
    __tablename__ = 'users'
    id : Mapped[int] = mapped_column(primary_key=True, index=True)
    username : Mapped[str] = mapped_column(unique=True)
    email : Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password : Mapped[str]=mapped_column(String)
    todos: Mapped[List["Todo"]] = relationship(back_populates="owner")



class Todo(Base):
    __tablename__ = "todos"
    id : Mapped[int] = mapped_column(primary_key=True, index=True)
    name : Mapped[str] = mapped_column(String)
    description : Mapped[str] = mapped_column(String)
    done : Mapped[bool] = mapped_column(Boolean)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    user_task_number : Mapped[int] = mapped_column(index=True)
    owner: Mapped["User"] = relationship(back_populates="todos")
    importance : Mapped[int]



