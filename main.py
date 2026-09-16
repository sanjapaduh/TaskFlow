from fastapi import FastAPI

from routers import testdoc, todos, auth
from database import engine
from models import Base


app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def hello(user:str):
    return{"message" : f"Hello {user}"}




# Connecting bd

app.include_router(testdoc.router)
app.include_router(todos.router)
app.include_router(auth.router)

