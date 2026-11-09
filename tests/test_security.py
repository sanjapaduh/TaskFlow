import os
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from httpx import AsyncClient

from core.security import ALGORITHM
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


@pytest.mark.parametrize(
    "payload",
    [
        {"username": "missing-user123", "password": "testpassw2ord"},
        {"username": "testuser1234", "password": "wrong-password"},
    ],
)
async def test_login_rejects_invalid_credentials(
    async_client: AsyncClient,
    test_user,
    payload,
):
    response = await async_client.post("/auth/login", json=payload)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password"}
    assert "access_token" not in response.json()


async def test_token_endpoint_rejects_invalid_credentials(
    async_client: AsyncClient,
    test_user,
):
    response = await async_client.post(
        "/auth/token",
        data={"username": test_user.username, "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "User is not authorized"}


async def test_protected_endpoint_rejects_missing_cookie(async_client: AsyncClient):
    response = await async_client.get("/todos/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.parametrize(
    "claims",
    [
        {"sub": "testuser1234", "id": 1, "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        {"sub": "testuser1234", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
    ],
)
async def test_protected_endpoint_rejects_invalid_jwt(
    async_client: AsyncClient,
    claims,
):
    token = jwt.encode(claims, os.environ["SECRET_KEY"], algorithm=ALGORITHM)

    response = await async_client.get(
        "/todos/me",
        cookies={"access_token": token},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "User is not authorized user"}


