import pytest
from httpx import AsyncClient

from main import app
from routers.security import get_current_user
from tests.conftest import test_user

pytestmark = pytest.mark.asyncio



async def override_get_currentuser():
    return {
        "id": 1,
        "username": "testuser1234",
        "email": "testuser@exam234ple.com",
        "password": "testpassw2ord"
    }


async def test_create_todo(async_client: AsyncClient, test_user):
    try:
        app.dependency_overrides[get_current_user] = override_get_currentuser
        payload = {
            "todo_request": {
                "name": "Test Todo",
                "description": "This is a test todo",
                "done": False,
                "importance": 1
            },
            "tag": {

                "name": "urgent",
                "color": "RED"
            }
        }
        response = await async_client.post("/todos", json=payload)
        if response.status_code != 200:
            print("DEBUG 422:", response.json())
        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()


async def test_get_todos(async_client: AsyncClient, test_todo):
    try:
        app.dependency_overrides[get_current_user] = override_get_currentuser
        response = await async_client.get("/todos")
        if response.status_code != 200:
            print("DEBUG 422:", response.json())
        assert response.status_code == 200
        data = response.json()
        todo_list = data["Your todos"]
        assert len(todo_list) == 1
        print("РЕНТГЕН ДАННЫХ:", data)
        assert todo_list[0]["name"] == "Test Todo"
    finally:
        app.dependency_overrides.clear()




# @pytest.mark.asyncio
async def test_login(async_client: AsyncClient):
    payload = {
        "username": "testuser1234",
        "password": "testpassw2ord"
    }
    response = await async_client.post("/auth/login", json=payload)

    assert response.status_code == 200
    data= response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    # assert data == {"success": True}

# @pytest.mark.asyncio
async def test_logout(async_client: AsyncClient):
    response = await async_client.post("/auth/logout")
    assert response.status_code == 200