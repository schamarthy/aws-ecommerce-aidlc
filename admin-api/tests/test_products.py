PRODUCT_PAYLOAD = {
    "name": "Widget",
    "price": 9.99,
    "sku": "WID-001",
    "description": "A test widget",
}


async def test_list_products_empty(client):
    resp = await client.get("/admin/products")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_product(client):
    resp = await client.post("/admin/products", json=PRODUCT_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["sku"] == "WID-001"
    assert data["status"] == "active"
    assert data["is_featured"] is False


async def test_create_duplicate_sku(client):
    await client.post("/admin/products", json=PRODUCT_PAYLOAD)
    resp = await client.post("/admin/products", json=PRODUCT_PAYLOAD)
    assert resp.status_code == 409


async def test_get_product(client):
    await client.post("/admin/products", json=PRODUCT_PAYLOAD)
    resp = await client.get("/admin/products/1")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Widget"


async def test_update_product(client):
    await client.post("/admin/products", json=PRODUCT_PAYLOAD)
    resp = await client.put("/admin/products/1", json={"price": 19.99, "updated_by": "admin"})
    assert resp.status_code == 200
    assert resp.json()["price"] == 19.99


async def test_update_status(client):
    await client.post("/admin/products", json=PRODUCT_PAYLOAD)
    resp = await client.patch("/admin/products/1/status", json={"status": "inactive"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "inactive"


async def test_update_featured(client):
    await client.post("/admin/products", json=PRODUCT_PAYLOAD)
    resp = await client.patch("/admin/products/1/featured", json={"is_featured": True})
    assert resp.status_code == 200
    assert resp.json()["is_featured"] is True


async def test_audit_log(client):
    await client.post("/admin/products", json=PRODUCT_PAYLOAD)
    await client.put("/admin/products/1", json={"price": 19.99, "updated_by": "admin"})
    resp = await client.get("/admin/products/1/audit")
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) >= 1
    field_names = {log["field_name"] for log in logs}
    assert "price" in field_names


async def test_delete_product(client):
    await client.post("/admin/products", json=PRODUCT_PAYLOAD)
    resp = await client.delete("/admin/products/1")
    assert resp.status_code == 204
    assert (await client.get("/admin/products/1")).status_code == 404
