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
        assert todo_list[0]["name"] == "Test Todo1"
    finally:
        app.dependency_overrides.clear()




# @pytest.mark.asyncio


# @pytest.mark.asyncio
async def test_put_todo(async_client: AsyncClient, test_todo):
    try:
        app.dependency_overrides[get_current_user] = override_get_currentuser
        payload = {
            "todo_request": {
                "name": "Updated Todo",
                "description": "This",
                "done": True,
                "importance": 2
            },
            "tag": {
                "name": "important",
                "color": "BLUE"
            }
        }
        response = await async_client.put(f"/todos/{test_todo.id}", json=payload)
        if response.status_code != 200:
            print("DEBUG 422:", response.json())
        assert response.status_code == 200
        data = response.json()
        print("РЕНТГЕН ДАННЫХ:", data)
        assert data == {"updated todo": "success"}
    finally:
        app.dependency_overrides.clear()


async def test_delete_todo(async_client: AsyncClient, test_todo):
    try:
        app.dependency_overrides[get_current_user] = override_get_currentuser
        response = await async_client.delete(f"/todos/{test_todo.id}")
        if response.status_code != 200:
            print("DEBUG 422:", response.json())
        assert response.status_code == 200
        data = response.json()
        print(data)
        assert data == {"deletion": "success"}
    finally:
        app.dependency_overrides.clear()

async def test_get_byId_todo(async_client: AsyncClient, test_todo):
    try:
        app.dependency_overrides[get_current_user] = override_get_currentuser
        response = await async_client.get(f"/todos/{test_todo.id}")
        if response.status_code != 200:
            print("DEBUG 422:", response.json())
        assert response.status_code == 200
        data = response.json()
        todo = data.get("todo")
        print("your todo:", todo)
        assert todo["name"] == "Test Todo1"
    finally:
        app.dependency_overrides.clear()

async def test_get_current_user_me(async_client: AsyncClient):
    app.dependency_overrides[get_current_user] = override_get_currentuser

    try:
        response = await async_client.get("/todos/me")
        print("DEBUG 422:", response.json())
        assert response.status_code == 200
        assert response.json() == {
            "message": "Cookie authentication works!",
            "user_data": {
                "id": 1,
                "username": "testuser1234",
                "email": "testuser@exam234ple.com",
                "password": "testpassw2ord",
            },
        }
    finally:
        app.dependency_overrides.pop(get_current_user, None)