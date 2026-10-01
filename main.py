from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from routers import todos, auth

from database import engine
from models import Base, User, Todo

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def hello():
    return {"Application": "Started"}

app.include_router(todos.router)
app.include_router(auth.router)