"""
Tests for U5 — Auth API
"""
from httpx import AsyncClient

from conftest import REGISTER_PAYLOAD


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------


async def test_register_success(client: AsyncClient):
    r = await client.post("/auth/register", json=REGISTER_PAYLOAD)
    assert r.status_code == 201
    data = r.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data
    assert data["user"]["email"] == "jane@example.com"
    assert data["user"]["name"] == "Jane Doe"
    assert "hashed_password" not in data["user"]


async def test_register_duplicate_email(client: AsyncClient):
    await client.post("/auth/register", json=REGISTER_PAYLOAD)
    r = await client.post("/auth/register", json=REGISTER_PAYLOAD)
    assert r.status_code == 409
    assert "already registered" in r.json()["detail"]


async def test_register_email_case_insensitive(client: AsyncClient):
    await client.post("/auth/register", json=REGISTER_PAYLOAD)
    r = await client.post("/auth/register", json={**REGISTER_PAYLOAD, "email": "JANE@EXAMPLE.COM"})
    assert r.status_code == 409


async def test_register_password_too_short(client: AsyncClient):
    r = await client.post("/auth/register", json={**REGISTER_PAYLOAD, "password": "short"})
    assert r.status_code == 422


async def test_register_invalid_email(client: AsyncClient):
    r = await client.post("/auth/register", json={**REGISTER_PAYLOAD, "email": "not-an-email"})
    assert r.status_code == 422


async def test_register_empty_name(client: AsyncClient):
    r = await client.post("/auth/register", json={**REGISTER_PAYLOAD, "name": "   "})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


async def test_login_success(client: AsyncClient):
    await client.post("/auth/register", json=REGISTER_PAYLOAD)
    r = await client.post("/auth/login", json={
        "email": REGISTER_PAYLOAD["email"],
        "password": REGISTER_PAYLOAD["password"],
    })
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["user"]["email"] == "jane@example.com"


async def test_login_wrong_password(client: AsyncClient):
    await client.post("/auth/register", json=REGISTER_PAYLOAD)
    r = await client.post("/auth/login", json={
        "email": REGISTER_PAYLOAD["email"],
        "password": "wrongpassword",
    })
    assert r.status_code == 401


async def test_login_nonexistent_user(client: AsyncClient):
    r = await client.post("/auth/login", json={
        "email": "nobody@example.com",
        "password": "anything123",
    })
    assert r.status_code == 401


async def test_login_email_case_insensitive(client: AsyncClient):
    await client.post("/auth/register", json=REGISTER_PAYLOAD)
    r = await client.post("/auth/login", json={
        "email": "JANE@EXAMPLE.COM",
        "password": REGISTER_PAYLOAD["password"],
    })
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# Profile (GET /auth/me)
# ---------------------------------------------------------------------------


async def _get_token(client: AsyncClient) -> str:
    r = await client.post("/auth/register", json=REGISTER_PAYLOAD)
    return r.json()["access_token"]


async def test_get_profile(client: AsyncClient):
    token = await _get_token(client)
    r = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "jane@example.com"
    assert data["name"] == "Jane Doe"


async def test_get_profile_no_token(client: AsyncClient):
    r = await client.get("/auth/me")
    assert r.status_code == 401


async def test_get_profile_invalid_token(client: AsyncClient):
    r = await client.get("/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# Update profile (PATCH /auth/me)
# ---------------------------------------------------------------------------


async def test_update_profile_name(client: AsyncClient):
    token = await _get_token(client)
    r = await client.patch(
        "/auth/me",
        json={"name": "Jane Smith"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Jane Smith"


async def test_update_profile_name_reflected_on_get(client: AsyncClient):
    token = await _get_token(client)
    await client.patch(
        "/auth/me",
        json={"name": "Updated Name"},
        headers={"Authorization": f"Bearer {token}"},
    )
    r = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.json()["name"] == "Updated Name"


async def test_update_profile_unauthenticated(client: AsyncClient):
    r = await client.patch("/auth/me", json={"name": "New Name"})
    assert r.status_code == 401


async def test_update_profile_empty_name(client: AsyncClient):
    token = await _get_token(client)
    r = await client.patch(
        "/auth/me",
        json={"name": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 422
