from dotenv import load_dotenv
from fastapi import FastAPI, Query
from pydantic import BaseModel

from database import engine
from models import Base
app = FastAPI()

Base.metadata.create_all(bind=engine)


toDoList = [1, 2, 3, 5]

class Todo(BaseModel):
    name : str
    description : str
    done : bool
    importance : int = Query(
        ge = 0,
        le = 10
    )

@app.get("/")
def hello(user:str):
    return{"message" : f"Hello {user}"}

@app.post("/addtodo")
def create_ToDo(todo : Todo):
    toDoList.append(todo)
    return{"message" : todo}

@app.get("/todos")
def all_todos():
    return {"message" : toDoList}


# Connecting bd
