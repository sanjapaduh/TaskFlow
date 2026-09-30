from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from routers import todos, auth
from database import engine, SessionLocal
from models import Base
from routers.dependencies import db_dependency

# app = FastAPI()


@asynccontextmanager
async def livespan(app: FastAPI):
    async with db_dependency.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(livespan=livespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def hello():
    return {"Application": "Started"}


# Connecting bd
app.include_router(todos.router)
app.include_router(auth.router)
