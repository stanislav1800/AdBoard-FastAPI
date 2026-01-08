
import pytest

@pytest.mark.asyncio
async def test_read_users_me(async_client, auth_headers):
    resp = await async_client.get("/api/v1/user/me", headers=auth_headers)
    assert resp.status_code == 200

    data = resp.json()
    assert "id" in data
    assert "email" in data

@pytest.mark.asyncio
async def test_get_user(async_client, auth_headers, user):
    resp = await async_client.get(f"/api/v1/user/{user.id}", headers=auth_headers)
    assert resp.status_code == 200

    data = resp.json()
    assert data["id"] == user.id

@pytest.mark.asyncio
async def test_get_user_not_found(async_client, auth_headers):
    resp = await async_client.get("/api/v1/user/999999", headers=auth_headers)
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_patch_user(async_client, auth_headers):
    resp = await async_client.patch(
        "/api/v1/user/me",
        json={"username": "NewName"},
        headers=auth_headers,
    )
    assert resp.status_code == 200

    data = resp.json()
    assert data["username"] == "NewName"

@pytest.mark.asyncio
async def test_put_user(async_client, auth_headers):
    resp = await async_client.put(
        "/api/v1/user/me",
        json={
            "username": "newusername",
            "email": "newemail@example.com",
            "avatar": "https://example.com/avatar.jpg",
            "location": "Moscow",
            "bio": "My bio",
            "phone_number": "+79991234567",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200

    data = resp.json()
    assert data["username"] == "newusername"
    assert data["email"] == "newemail@example.com"

@pytest.mark.asyncio
async def test_delete_user(async_client, auth_headers):
    resp = await async_client.delete("/api/v1/user/me", headers=auth_headers)
    assert resp.status_code == 204

@pytest.mark.asyncio
async def test_get_comments(async_client, auth_headers, user):
    resp = await async_client.get(f"/api/v1/user/{user.id}/comments", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

@pytest.mark.asyncio
async def test_create_comment(async_client, auth_headers, user2):
    payload = {"score": 5, "comment": "Great user!"}
    resp = await async_client.post(
        f"/api/v1/user/{user2.id}/comments",
        json=payload,
        headers=auth_headers,
    )
    assert resp.status_code == 200

    data = resp.json()
    assert data["score"] == 5
    assert data["comment"] == "Great user!"

@pytest.mark.asyncio
async def test_cannot_comment_yourself(async_client, auth_headers, user):
    payload = {"score": 5, "comment": "Hi me!"}
    resp = await async_client.post(
        f"/api/v1/user/{user.id}/comments",
        json=payload,
        headers=auth_headers,
    )
    assert resp.status_code == 400
