import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:root@localhost:5432/test_db"

engine_test = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    # Создаем таблицы перед тестом
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

# 2. Указываем FastAPI подменить зависимость!
app.dependency_overrides[setup_db] = override_get_db