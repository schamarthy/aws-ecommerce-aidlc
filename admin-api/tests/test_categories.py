import pytest


async def test_list_categories_empty(client):
    resp = await client.get("/admin/categories")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_category(client):
    resp = await client.post("/admin/categories", json={"name": "Electronics", "description": "Gadgets"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Electronics"
    assert data["id"] == 1


async def test_create_duplicate_category(client):
    await client.post("/admin/categories", json={"name": "Electronics"})
    resp = await client.post("/admin/categories", json={"name": "Electronics"})
    assert resp.status_code == 409


async def test_get_category(client):
    await client.post("/admin/categories", json={"name": "Books"})
    resp = await client.get("/admin/categories/1")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Books"


async def test_get_category_not_found(client):
    resp = await client.get("/admin/categories/999")
    assert resp.status_code == 404


async def test_update_category(client):
    await client.post("/admin/categories", json={"name": "Books"})
    resp = await client.put("/admin/categories/1", json={"name": "Updated Books"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Books"


async def test_delete_category(client):
    await client.post("/admin/categories", json={"name": "Temp"})
    resp = await client.delete("/admin/categories/1")
    assert resp.status_code == 204
    resp2 = await client.get("/admin/categories/1")
    assert resp2.status_code == 404
