
import pytest
from fastapi import status

from app.core.security import create_refresh_token

@pytest.mark.asyncio
async def test_register_user(async_client):
    payload = {
        "username": "newuser",
        "password1": "password123",
        "password2": "password123"
    }
    resp = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == status.HTTP_201_CREATED

    resp2 = await async_client.post(
        "/api/v1/auth/token",
        data={"username": payload["username"], "password": payload["password1"]},
    )
    tokens = resp2.json()
    assert "access_token" in tokens
    
    resp3 = await async_client.get(
        "/api/v1/user/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    data3 = resp3.json()
    assert data3["username"] == payload["username"]


@pytest.mark.asyncio
async def test_register_user_password_mismatch(async_client):
    payload = {
        "username": "user2",
        "password1": "pass1",
        "password2": "pass2"
    }
    resp = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_token_success(async_client, user):
    form_data = {
        "username": user.username,
        "password": "user"
    }
    resp = await async_client.post("/api/v1/auth/token", data=form_data)
    assert resp.status_code == status.HTTP_200_OK

    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_token_invalid_password(async_client, user):
    form_data = {
        "username": user.username,
        "password": "wrongpassword"
    }
    resp = await async_client.post("/api/v1/auth/token", data=form_data)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    data = resp.json()
    assert data["detail"] == "Incorrect username or password"


@pytest.mark.asyncio
async def test_token_refresh_success(async_client, user):
    refresh_token = create_refresh_token({"sub": str(user.id)})
    resp = await async_client.post("/api/v1/auth/token/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == status.HTTP_200_OK

    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_token_refresh_invalid(async_client):
    resp = await async_client.post("/api/v1/auth/token/refresh", json={"refresh_token": "invalidtoken"})
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    data = resp.json()
    assert data["detail"] == "Недопустимый refresh token"
