import time
from contextlib import asynccontextmanager

from urllib.request import Request

from fastapi import FastAPI
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from database import Base, engine
from routers import todos, auth


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def hello():
    return FileResponse("static/index.html")


@app.middleware("http")
async def middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


app.include_router(todos.router)
app.include_router(auth.router)
