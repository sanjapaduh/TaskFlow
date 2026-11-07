import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from models import User, Todo
from routers.security import bcrypt_context

load_dotenv(".env.test")

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]

engine_test = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestingSessionLocal = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db

    try:
        # Создаем таблицы перед тестом
        async with engine_test.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield
    finally:
        async with engine_test.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def test_user(db_session):
    hashed_password = bcrypt_context.hash("testpassw2ord")
    user = User(
        username="testuser1234",
        email="testuser@exam234ple.com",
        hashed_password=hashed_password
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def test_todo(db_session, test_user):
    todo = Todo(
        name="Test Todo",
        description="This is a test todo",
        done=False,
        importance=1,
        user_task_number=1,
        user_id=test_user.id
    )

    db_session.add(todo)
    await db_session.commit()
    await db_session.refresh(todo)
    return todo
