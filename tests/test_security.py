from urllib import response

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from routers.dependencies import get_current_user
from main import app
from models import Todo


@pytest.mark.asyncio
async def test_create_user(async_client: AsyncClient, db_session: AsyncSession):
    pass


@pytest.mark.asyncio
async def test_get_all_users(db_session: AsyncSession):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as async_client:
        app.dependency_overrides[get_current_user] = lambda: {"id": 1, "username": "testuser"}
        test_todo = Todo(name="tgv", user_id=1)
        db_session.add_all(test_todo)
        await db_session.commit()
        await db_session.refresh(test_todo)

        response = await async_client.get("/todos")

        assert response.status_code == 200

        data = response.json()

        assert "Your data " in data
        assert isinstance(data, list)
        assert len(data) == 1

        first_todo = data[0]
        assert "id" in first_todo
        assert first_todo["name"] == "alice"
        assert first_todo["user_id"] == 1

        app.dependency_overrides.clear()
