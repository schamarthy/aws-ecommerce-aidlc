PRODUCT_PAYLOAD = {"name": "Widget", "price": 9.99, "sku": "WID-001"}


async def _create_product(client):
    resp = await client.post("/admin/products", json=PRODUCT_PAYLOAD)
    assert resp.status_code == 201
    return resp.json()["id"]


async def test_get_inventory_creates_default(client):
    pid = await _create_product(client)
    resp = await client.get(f"/admin/inventory/{pid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["quantity"] == 0
    assert data["low_stock_threshold"] == 10


async def test_update_inventory(client):
    pid = await _create_product(client)
    resp = await client.put(f"/admin/inventory/{pid}", json={"quantity": 50, "actor": "admin"})
    assert resp.status_code == 200
    assert resp.json()["quantity"] == 50


async def test_stock_history(client):
    pid = await _create_product(client)
    await client.put(f"/admin/inventory/{pid}", json={"quantity": 50, "actor": "admin"})
    await client.put(f"/admin/inventory/{pid}", json={"quantity": 30, "actor": "admin", "reason": "sale"})
    resp = await client.get(f"/admin/inventory/{pid}/history")
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) == 2
    assert logs[0]["adjustment"] == -20


async def test_update_threshold(client):
    pid = await _create_product(client)
    resp = await client.patch(f"/admin/inventory/{pid}/threshold", json={"low_stock_threshold": 5})
    assert resp.status_code == 200
    assert resp.json()["low_stock_threshold"] == 5


async def test_dashboard(client):
    pid = await _create_product(client)
    await client.put(f"/admin/inventory/{pid}", json={"quantity": 3, "actor": "admin"})
    await client.patch(f"/admin/inventory/{pid}/threshold", json={"low_stock_threshold": 5})
    resp = await client.get("/admin/inventory")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["is_low_stock"] is True


async def test_bulk_update(client):
    pid1 = await _create_product(client)
    resp2 = await client.post("/admin/products", json={"name": "Gadget", "price": 5.0, "sku": "GAD-001"})
    pid2 = resp2.json()["id"]
    resp = await client.post(
        "/admin/inventory/bulk-update",
        json={"updates": [
            {"product_id": pid1, "quantity": 100, "actor": "batch"},
            {"product_id": pid2, "quantity": 200, "actor": "batch"},
        ]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["quantity"] == 100
    assert data[1]["quantity"] == 200
