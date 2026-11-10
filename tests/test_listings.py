from io import BytesIO

import pytest
from unittest.mock import AsyncMock

from app.models import Category, Listing, ListingImage

@pytest.mark.asyncio
async def test_create_listing(async_client, auth_headers):
    payload = {
        "title": "iPhone 15",
        "description": "New phone",
        "price": 1000,
        "condition": "new",
        "location": "Moscow",
        "category_ids": [],
    }
    response = await async_client.post(
        "/api/v1/listing",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "iPhone 15"
    assert data["price"] == 1000
    assert data["status"] == "moderation"

@pytest.mark.asyncio
async def test_update_listing_only_owner(
    async_client,
    auth_headers,
):
    create_resp = await async_client.post(
        "/api/v1/listing",
        json={
            "title": "Old title",
            "description": "desc",
            "price": 10,
            "condition": "used",
            "location": "SPB",
            "category_ids": [],
        },
        headers=auth_headers,
    )

    listing_id = create_resp.json()["id"]

    update_resp = await async_client.patch(
        f"/api/v1/listing/{listing_id}",
        json={"title": "New title"},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "New title"

@pytest.mark.asyncio
async def test_only_admin_can_see_all_listings(
    async_client,
    auth_headers,
):
    response = await async_client.get(
        "/api/v1/listing",
        headers=auth_headers,
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_admin_can_see_all_listings(
    async_client,
    admin_headers,
):
    response = await async_client.get(
        "/api/v1/listing",
        headers=admin_headers,
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_upload_listing_images(
    async_client,
    auth_headers,
):
    resp = await async_client.post(
        "/api/v1/listing",
        json={
            "title": "With images",
            "description": "desc",
            "price": 50,
            "condition": "new",
            "location": "Kazan",
            "category_ids": [],
        },
        headers=auth_headers,
    )
    listing_id = resp.json()["id"]

    files = [
        ("files", ("img1.jpg", BytesIO(b"image1"), "image/jpeg")),
        ("files", ("img2.jpg", BytesIO(b"image2"), "image/jpeg")),
    ]

    upload_resp = await async_client.post(
        f"/api/v1/listing/{listing_id}/images",
        files=files,
        headers=auth_headers,
    )
    assert upload_resp.status_code == 201

    data = upload_resp.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert "id" in data[0]
    assert "image" in data[0]

@pytest.mark.asyncio
async def test_user_cannot_approve_listing(
    async_client,
    auth_headers,
):
    create_resp = await async_client.post(
        "/api/v1/listing",
        json={
            "title": "Needs moderation",
            "description": "desc",
            "price": 100,
            "condition": "new",
            "location": "Moscow",
            "category_ids": [],
        },
        headers=auth_headers,
    )

    listing_id = create_resp.json()["id"]

    resp = await async_client.post(
        f"/api/v1/listing/{listing_id}/moderated",
        json={
            "action": "active",
            "reason": "Все ок",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_moderator_can_approve_listing(
    async_client,
    auth_headers,
    moderator_headers,
):
    create_resp = await async_client.post(
        "/api/v1/listing",
        json={
            "title": "To approve",
            "description": "desc",
            "price": 200,
            "condition": "new",
            "location": "SPB",
            "category_ids": [],
        },
        headers=auth_headers,
    )

    listing_id = create_resp.json()["id"]

    approve_resp = await async_client.post(
        f"/api/v1/listing/{listing_id}/moderated",
        json={
            "action": "active",
            "reason": "Все ок",
        },
        headers=moderator_headers,
    )
    assert approve_resp.status_code == 201
    assert approve_resp.json()["action"] == "active"

@pytest.mark.asyncio
async def test_moderator_can_reject_listing(
    async_client,
    auth_headers,
    moderator_headers,
):
    create_resp = await async_client.post(
        "/api/v1/listing",
        json={
            "title": "Bad listing",
            "description": "spam",
            "price": 1,
            "condition": "used",
            "location": "Nowhere",
            "category_ids": [],
        },
        headers=auth_headers,
    )

    listing_id = create_resp.json()["id"]

    reject_resp = await async_client.post(
        f"/api/v1/listing/{listing_id}/moderated",
        json={
            "action": "rejected",
            "reason": "Spam",
        },
        headers=moderator_headers,
    )
    assert reject_resp.status_code == 201

    data = reject_resp.json()
    assert data["action"] == "rejected"
    assert data["reason"] == "Spam"

@pytest.mark.asyncio
async def test_cannot_approve_already_approved(
    async_client,
    auth_headers,
    moderator_headers,
):
    create_resp = await async_client.post(
        "/api/v1/listing",
        json={
            "title": "Already approved",
            "description": "ok",
            "price": 300,
            "condition": "new",
            "location": "Kazan",
            "category_ids": [],
        },
        headers=auth_headers,
    )
    listing_id = create_resp.json()["id"]

    await async_client.post(
        f"/api/v1/listing/{listing_id}/moderated",
        json={
            "action": "active",
            "reason": "Все ок",
        },
        headers=moderator_headers,
    )
    resp = await async_client.post(
        f"/api/v1/listing/{listing_id}/moderated",
        json={
            "action": "active",
            "reason": "Все ок",
        },
        headers=moderator_headers,
    )
    assert resp.status_code == 400

@pytest.mark.asyncio
async def test_admin_can_moderate(
    async_client,
    auth_headers,
    admin_headers,
):
    create_resp = await async_client.post(
        "/api/v1/listing",
        json={
            "title": "Admin approves",
            "description": "desc",
            "price": 500,
            "condition": "new",
            "location": "Moscow",
            "category_ids": [],
        },
        headers=auth_headers,
    )
    listing_id = create_resp.json()["id"]

    resp = await async_client.post(
        f"/api/v1/listing/{listing_id}/moderated",
        json={
            "action": "active",
            "reason": "Все ок",
        },
        headers=admin_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["action"] == "active"

@pytest.mark.asyncio
async def test_owner_can_delete_listing(
    async_client,
    auth_headers,
):
    create = await async_client.post(
        "/api/v1/listing",
        json={
            "title": "Delete me",
            "description": "desc",
            "price": 100,
            "condition": "new",
            "location": "Moscow",
            "category_ids": [],
        },
        headers=auth_headers,
    )
    assert create.status_code == 201
    listing_id = create.json()["id"]

    resp = await async_client.delete(
        f"/api/v1/listing/{listing_id}",
        headers=auth_headers,
    )
    assert resp.status_code == 204

@pytest.mark.asyncio
async def test_deleted_listing_not_visible_publicly(
    async_client,
    auth_headers,
):
    create = await async_client.post(
        "/api/v1/listing",
        json={
            "title": "Invisible",
            "description": "desc",
            "price": 100,
            "condition": "new",
            "location": "SPB",
            "category_ids": [],
        },
        headers=auth_headers,
    )
    listing_id = create.json()["id"]

    await async_client.delete(
        f"/api/v1/listing/{listing_id}",
        headers=auth_headers,
    )

    resp = await async_client.get(f"/api/v1/listing/{listing_id}")
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_cannot_delete__listing(
    async_client,
    auth_headers,
    auth2_headers,
):
    create = await async_client.post(
        "/api/v1/listing",
        json={
            "title": "Not yours",
            "description": "desc",
            "price": 100,
            "condition": "new",
            "location": "Kazan",
            "category_ids": [],
        },
        headers=auth_headers,
    )
    listing_id = create.json()["id"]

    resp = await async_client.delete(
        f"/api/v1/listing/{listing_id}",
        headers=auth2_headers,
    )
    assert resp.status_code in (403, 404)

@pytest.mark.asyncio
async def test_admin_can_delete_any_listing(
    async_client,
    auth_headers,
    admin_headers,
):
    create = await async_client.post(
        "/api/v1/listing",
        json={
            "title": "Admin deletes",
            "description": "desc",
            "price": 100,
            "condition": "new",
            "location": "City",
            "category_ids": [],
        },
        headers=auth_headers,
    )
    listing_id = create.json()["id"]

    resp = await async_client.delete(
        f"/api/v1/listing/{listing_id}",
        headers=admin_headers,
    )
    assert resp.status_code == 204

@pytest.mark.asyncio
async def test_cannot_delete_listing_twice(
    async_client,
    auth_headers,
):
    create = await async_client.post(
        "/api/v1/listing",
        json={
            "title": "Delete twice",
            "description": "desc",
            "price": 100,
            "condition": "new",
            "location": "City",
            "category_ids": [],
        },
        headers=auth_headers,
    )
    listing_id = create.json()["id"]

    await async_client.delete(
        f"/api/v1/listing/{listing_id}",
        headers=auth_headers,
    )

    resp = await async_client.delete(
        f"/api/v1/listing/{listing_id}",
        headers=auth_headers,
    )
    assert resp.status_code in (404, 400)

@pytest.mark.asyncio
async def test_images_removed_when_listing_deleted(
    async_client,
    auth_headers,
    tmp_path,
):
    create = await async_client.post(
        "/api/v1/listing",
        json={
            "title": "With images",
            "description": "desc",
            "price": 100,
            "condition": "new",
            "location": "City",
            "category_ids": [],
        },
        headers=auth_headers,
    )
    listing_id = create.json()["id"]

    upload = await async_client.post(
        f"/api/v1/listing/{listing_id}/images",
        files={"files": ("img.jpg", b"fake-image", "image/jpeg")},
        headers=auth_headers,
    )
    assert upload.status_code == 201
    image_id = upload.json()[0]["id"]

    delete = await async_client.delete(
        f"/api/v1/listing/{listing_id}",
        headers=auth_headers,
    )
    assert delete.status_code == 204

    check = await async_client.get(f"/api/v1/listing/{image_id}/images")
    assert check.status_code == 404

@pytest.mark.asyncio
async def test_get_my_listings(async_client, auth_headers, auth2_headers):
    my_ids = []
    for i in range(2):
        resp = await async_client.post(
            "/api/v1/listing",
            json={
                "title": f"My listing {i}",
                "description": "desc",
                "price": 100 + i,
                "condition": "new",
                "location": "City",
                "category_ids": [],
            },
            headers=auth_headers,
        )
        my_ids.append(resp.json()["id"])

    for i in range(2):
        await async_client.post(
            "/api/v1/listing",
            json={
                "title": f"Other listing {i}",
                "description": "desc",
                "price": 200 + i,
                "condition": "used",
                "location": "City",
                "category_ids": [],
            },
            headers=auth2_headers,
        )

    resp = await async_client.get("/api/v1/listing/my_listings", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    returned_ids = {item["id"] for item in data}
    for id in my_ids:
        assert id in returned_ids

@pytest.mark.asyncio
async def test_get_moderation_listings_only_admin(async_client, auth_headers, admin_headers):
    await async_client.post(
        "/api/v1/listing",
        json={
            "title": "M1",
            "description": "desc",
            "price": 10,
            "condition": "new",
            "location": "City",
            "category_ids": [],
        },
        headers=auth_headers,
    )
    await async_client.post(
        "/api/v1/listing",
        json={
            "title": "M2",
            "description": "desc",
            "price": 20,
            "condition": "new",
            "location": "City",
            "category_ids": [],
        },
        headers=admin_headers,
    )

    resp_user = await async_client.get("/api/v1/listing/moderation", headers=auth_headers)
    assert resp_user.status_code == 403

    resp_admin = await async_client.get("/api/v1/listing/moderation", headers=admin_headers)
    assert resp_admin.status_code == 200
    
    data = resp_admin.json()
    assert all(item["status"] == "moderation" for item in data)

@pytest.mark.asyncio
async def test_add_listing_to_favorites(
    async_client,
    auth_headers,
):
    create_resp = await async_client.post(
        "/api/v1/listing",
        json={
            "title": "Favorite me",
            "description": "desc",
            "price": 100,
            "condition": "new",
            "location": "Moscow",
            "category_ids": [],
        },
        headers=auth_headers,
    )
    listing_id = create_resp.json()["id"]

    resp = await async_client.post(
        f"/api/v1/listing/{listing_id}/favorites",
        headers=auth_headers,
    )
    assert resp.status_code == 201

@pytest.mark.asyncio
async def test_cannot_add_same_listing_twice(
    async_client,
    auth_headers,
):
    create = await async_client.post(
        "/api/v1/listing",
        json={
            "title": "Duplicate favorite",
            "description": "desc",
            "price": 200,
            "condition": "new",
            "location": "SPB",
            "category_ids": [],
        },
        headers=auth_headers,
    )
    listing_id = create.json()["id"]

    await async_client.post(
        f"/api/v1/listing/{listing_id}/favorites",
        headers=auth_headers,
    )

    resp = await async_client.post(
        f"/api/v1/listing/{listing_id}/favorites",
        headers=auth_headers,
    )
    assert resp.status_code in (400, 409)

@pytest.mark.asyncio
async def test_get_my_favorites(
    async_client,
    auth_headers,
):
    ids = []
    for i in range(2):
        resp = await async_client.post(
            "/api/v1/listing",
            json={
                "title": f"Fav {i}",
                "description": "desc",
                "price": 100 + i,
                "condition": "new",
                "location": "City",
                "category_ids": [],
            },
            headers=auth_headers,
        )
        ids.append(resp.json()["id"])

    for lid in ids:
        await async_client.post(
            f"/api/v1/listing/{lid}/favorites",
            headers=auth_headers,
        )

    resp = await async_client.get(
        "/api/v1/listing/favorites",
        headers=auth_headers,
    )
    assert resp.status_code == 200

    data = resp.json()
    assert len(data) == 2
    assert {item["id"] for item in data} == set(ids)

@pytest.mark.asyncio
async def test_remove_from_favorites(
    async_client,
    auth_headers,
):
    create = await async_client.post(
        "/api/v1/listing",
        json={
            "title": "Remove me",
            "description": "desc",
            "price": 123,
            "condition": "new",
            "location": "Kazan",
            "category_ids": [],
        },
        headers=auth_headers,
    )
    listing_id = create.json()["id"]

    await async_client.post(
        f"/api/v1/listing/{listing_id}/favorites",
        headers=auth_headers,
    )

    resp = await async_client.delete(
        f"/api/v1/listing/{listing_id}/favorites",
        headers=auth_headers,
    )
    assert resp.status_code == 204

@pytest.mark.asyncio
async def test_remove_non_existing_favorite(
    async_client,
    auth_headers,
):
    resp = await async_client.delete(
        "/api/v1/listings/999999/favorites",
        headers=auth_headers,
    )
    assert resp.status_code in (404, 400)

@pytest.mark.asyncio
async def test_favorite_requires_auth(async_client):
    resp = await async_client.post("/api/v1/listing/1/favorites")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_listing_detail(async_client, auth_headers, listing):
    resp = await async_client.get(f"/api/v1/listing/{listing.id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == listing.id

@pytest.mark.asyncio
async def test_patch_listing_categories(async_client, auth_headers, session, listing):
    cat1 = Category(name="Phones", slug="phones", order=1)
    cat2 = Category(name="Laptops", slug="laptops", order=2)
    session.add_all([cat1, cat2])
    await session.commit()

    resp = await async_client.patch(
        f"/api/v1/listing/{listing.id}",
        json={"categories": [cat1.id, cat2.id]},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert {c["id"] for c in resp.json()["categories"]} == {cat1.id, cat2.id}

    resp = await async_client.patch(
        f"/api/v1/listing/{listing.id}",
        json={"categories": [cat2.id]},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert [c["id"] for c in resp.json()["categories"]] == [cat2.id]

@pytest.mark.asyncio
async def test_uploaded_files_get_unique_safe_names(async_client, auth_headers, listing):
    files = [
        ("files", ("../../evil.jpg", BytesIO(b"image1"), "image/jpeg")),
        ("files", ("../../evil.jpg", BytesIO(b"image2"), "image/jpeg")),
    ]
    resp = await async_client.post(
        f"/api/v1/listing/{listing.id}/images",
        files=files,
        headers=auth_headers,
    )
    assert resp.status_code == 201

    paths = [img["image"] for img in resp.json()]
    assert len(set(paths)) == 2
    assert all(".." not in p and "/" not in p for p in paths)

@pytest.mark.asyncio
async def test_cannot_set_primary_image_of_other_listing(
    async_client, auth_headers, session, listing, user2
):
    foreign = Listing(title="Foreign", description="d", price=1, condition="new", location="City", user_id=user2.id)
    session.add(foreign)
    await session.commit()
    image = ListingImage(listing_id=foreign.id, image="x.jpg", order=1, is_primary=False)
    session.add(image)
    await session.commit()

    resp = await async_client.post(
        f"/api/v1/listing/{listing.id}/images/{image.id}/primary",
        headers=auth_headers,
    )
    assert resp.status_code == 404

    await session.refresh(image)
    assert image.is_primary is False

@pytest.mark.asyncio
async def test_owner_can_delete_image(async_client, auth_headers, auth2_headers, session, listing):
    image = ListingImage(listing_id=listing.id, image="missing.jpg", order=1, is_primary=True)
    session.add(image)
    await session.commit()

    resp = await async_client.delete(f"/api/v1/listing/images/{image.id}", headers=auth2_headers)
    assert resp.status_code == 403

    resp = await async_client.delete(f"/api/v1/listing/images/{image.id}", headers=auth_headers)
    assert resp.status_code == 204

@pytest.mark.asyncio
async def test_image_of_hidden_listing_not_public(async_client, auth2_headers, session, listing):
    image = ListingImage(listing_id=listing.id, image="x.jpg", order=1, is_primary=True)
    session.add(image)
    await session.commit()

    resp = await async_client.get(f"/api/v1/listing/{image.id}/images", headers=auth2_headers)
    assert resp.status_code == 404

@pytest.mark.asyncio
@pytest.mark.parametrize("action, subject_part", [("active", "прошло"), ("rejected", "отклонено")])
async def test_moderation_sends_email_via_queue(
    monkeypatch, session, async_client, moderator_headers, user, listing,
    action, subject_part,
):
    user.email = "owner@test.com"
    listing.title = "<b>Bike</b>"
    await session.commit()

    send = AsyncMock()
    monkeypatch.setattr("app.services.email.EmailService.send", send)

    resp = await async_client.post(
        f"/api/v1/listing/{listing.id}/moderated",
        json={"action": action, "reason": "ok"},
        headers=moderator_headers,
    )
    assert resp.status_code == 201

    send.assert_awaited_once()
    kwargs = send.await_args.kwargs
    assert kwargs["recipients"] == ["owner@test.com"]
    assert subject_part in kwargs["subject"]
    assert "&lt;b&gt;Bike&lt;/b&gt;" in kwargs["body"]
