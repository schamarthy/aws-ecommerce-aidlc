TOKEN = "test-session-token-abc123"
HEADERS = {"X-Session-Token": TOKEN}


async def test_get_empty_cart(client):
    resp = await client.get("/cart", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["session_token"] == TOKEN
    assert data["items"] == []
    assert data["subtotal"] == 0.0
    assert data["item_count"] == 0


async def test_missing_token(client):
    resp = await client.get("/cart")
    assert resp.status_code == 422


async def test_add_item(client):
    resp = await client.post("/cart/items", json={"product_id": 1, "quantity": 2}, headers=HEADERS)
    assert resp.status_code == 201
    data = resp.json()
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert item["product_id"] == 1
    assert item["quantity"] == 2
    assert item["unit_price"] == 999.99
    assert item["line_total"] == 1999.98
    assert data["item_count"] == 2


async def test_add_item_accumulates(client):
    await client.post("/cart/items", json={"product_id": 1, "quantity": 2}, headers=HEADERS)
    resp = await client.post("/cart/items", json={"product_id": 1, "quantity": 3}, headers=HEADERS)
    assert resp.status_code == 201
    assert resp.json()["items"][0]["quantity"] == 5


async def test_add_item_exceeds_stock(client):
    resp = await client.post("/cart/items", json={"product_id": 1, "quantity": 99}, headers=HEADERS)
    assert resp.status_code == 409


async def test_add_out_of_stock_product(client):
    # product 2 has stock=2, add exactly 2 then try 1 more
    await client.post("/cart/items", json={"product_id": 2, "quantity": 2}, headers=HEADERS)
    resp = await client.post("/cart/items", json={"product_id": 2, "quantity": 1}, headers=HEADERS)
    assert resp.status_code == 409


async def test_add_inactive_product(client):
    resp = await client.post("/cart/items", json={"product_id": 3, "quantity": 1}, headers=HEADERS)
    assert resp.status_code == 404


async def test_update_item(client):
    add_resp = await client.post("/cart/items", json={"product_id": 1, "quantity": 1}, headers=HEADERS)
    item_id = add_resp.json()["items"][0]["id"]
    resp = await client.patch(f"/cart/items/{item_id}", json={"quantity": 5}, headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["items"][0]["quantity"] == 5


async def test_update_item_exceeds_stock(client):
    add_resp = await client.post("/cart/items", json={"product_id": 1, "quantity": 1}, headers=HEADERS)
    item_id = add_resp.json()["items"][0]["id"]
    resp = await client.patch(f"/cart/items/{item_id}", json={"quantity": 100}, headers=HEADERS)
    assert resp.status_code == 409


async def test_remove_item(client):
    add_resp = await client.post("/cart/items", json={"product_id": 1, "quantity": 1}, headers=HEADERS)
    item_id = add_resp.json()["items"][0]["id"]
    resp = await client.delete(f"/cart/items/{item_id}", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["items"] == []


async def test_clear_cart(client):
    await client.post("/cart/items", json={"product_id": 1, "quantity": 1}, headers=HEADERS)
    await client.post("/cart/items", json={"product_id": 2, "quantity": 1}, headers=HEADERS)
    resp = await client.delete("/cart", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["items"] == []
    assert resp.json()["subtotal"] == 0.0


async def test_cart_isolation(client):
    """Different session tokens have separate carts."""
    await client.post("/cart/items", json={"product_id": 1, "quantity": 2}, headers=HEADERS)
    other = {"X-Session-Token": "other-session-xyz"}
    resp = await client.get("/cart", headers=other)
    assert resp.json()["items"] == []


async def test_subtotal(client):
    await client.post("/cart/items", json={"product_id": 1, "quantity": 2}, headers=HEADERS)
    await client.post("/cart/items", json={"product_id": 2, "quantity": 1}, headers=HEADERS)
    resp = await client.get("/cart", headers=HEADERS)
    data = resp.json()
    expected = round(999.99 * 2 + 39.99 * 1, 2)
    assert data["subtotal"] == expected
    assert data["item_count"] == 3
