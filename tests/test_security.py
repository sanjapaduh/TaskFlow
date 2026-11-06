from urllib import response

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from routers.dependencies import get_current_user
from main import app
from models import Todo

pytestmark = pytest.mark.asyncio



@pytest.mark.asyncio
async def test_register(async_client: AsyncClient):
    payload = {
        "username": "testuser1234",
        "email": "testuser@exam234ple.com",
        "password": "testpassw2ord"

    }

    response = await async_client.post("/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data == {"success": True}




@pytest.mark.asyncio
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

@pytest.mark.asyncio
async def test_logout(async_client: AsyncClient):
    response = await async_client.post("/auth/logout")
    assert response.status_code == 200