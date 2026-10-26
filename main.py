import time
from contextlib import asynccontextmanager

from urllib.request import Request

from fastapi import FastAPI

from routers import todos, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def hello():
    return {"Application": "Started"}


@app.middleware("http")
async def middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


app.include_router(todos.router)
app.include_router(auth.router)
