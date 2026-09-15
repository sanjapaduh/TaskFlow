from sqlalchemy.orm import relationship

from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True, index=True)
    todos = relationship('Todo', back_populates='owner')


class Todo(Base):
    __tablename__ = "todo"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    done = Column(Boolean)
    user_id = Column(Integer, ForeignKey('user.id'))
    owner = relationship('User', back_populates='todos')



