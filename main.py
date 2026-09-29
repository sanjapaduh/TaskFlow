from fastapi import FastAPI
from starlette import status
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.status import HTTP_302_FOUND
from starlette.templating import Jinja2Templates

from routers import todos, auth
from database import engine, SessionLocal
from models import Base

app = FastAPI()

Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def hello():
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)




# Connecting bd

app.include_router(todos.router)
app.include_router(auth.router)


