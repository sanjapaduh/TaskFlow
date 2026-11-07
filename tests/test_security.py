import pytest
from httpx import AsyncClient

from tests.conftest import test_user

pytestmark = pytest.mark.asyncio


# @pytest.mark.asyncio
async def test_register(async_client: AsyncClient):
    payload = {
        "username": "testuser2",
        "email": "testuser@exam2ple.com",
        "password": "testpassw2ord"

    }

    response = await async_client.post("/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data == {"success": True}




# @pytest.mark.asyncio
async def test_login(async_client: AsyncClient, test_user):
    payload = {"username": test_user.username, "password": "testpassw2ord"}
    response = await async_client.post("/auth/login", json=payload)

    assert response.status_code == 200
    data= response.json()

    print("LOCATION data IS HEAR: ", data)
    print(" request IS HEAR: ", response.json())
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    # assert data == {"success": True}

# @pytest.mark.asyncio
async def test_logout(async_client: AsyncClient):
    response = await async_client.post("/auth/logout")
    assert response.status_code == 200