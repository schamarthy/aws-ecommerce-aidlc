"""
Tests for U4 — Checkout & Orders API
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import sessionmaker

from app.models.admin_mirror import MirrorInventory
from app.models.cart_mirror import MirrorCart, MirrorCartItem
from conftest import (
    TOKEN,
    AdminSession,
    CartSession,
    HEADERS,
    admin_engine,
    cart_engine,
)

SHIPPING = {
    "shipping_name": "Jane Doe",
    "shipping_email": "jane@example.com",
    "shipping_address": "123 Main St, Springfield",
}

OTHER_TOKEN = "other-session-token-xyz"
OTHER_HEADERS = {"X-Session-Token": OTHER_TOKEN}


# ---------------------------------------------------------------------------
# Checkout
# ---------------------------------------------------------------------------


async def test_checkout_creates_order(client: AsyncClient):
    r = await client.post("/orders/checkout", json=SHIPPING, headers=HEADERS)
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "confirmed"
    assert data["shipping_name"] == "Jane Doe"
    assert data["shipping_email"] == "jane@example.com"
    assert len(data["items"]) == 2


async def test_checkout_total_correct(client: AsyncClient):
    r = await client.post("/orders/checkout", json=SHIPPING, headers=HEADERS)
    assert r.status_code == 201
    # 999.99 * 1 + 39.99 * 2 = 1079.97
    assert r.json()["total_amount"] == pytest.approx(1079.97, abs=0.01)


async def test_checkout_items_snapshot(client: AsyncClient):
    r = await client.post("/orders/checkout", json=SHIPPING, headers=HEADERS)
    items = {i["product_sku"]: i for i in r.json()["items"]}
    assert items["LAP-001"]["unit_price"] == pytest.approx(999.99)
    assert items["LAP-001"]["quantity"] == 1
    assert items["BK-001"]["unit_price"] == pytest.approx(39.99)
    assert items["BK-001"]["quantity"] == 2


async def test_checkout_deducts_inventory(client: AsyncClient):
    await client.post("/orders/checkout", json=SHIPPING, headers=HEADERS)
    db = AdminSession()
    inv1 = db.query(MirrorInventory).filter_by(product_id=1).first()
    inv2 = db.query(MirrorInventory).filter_by(product_id=2).first()
    db.close()
    assert inv1.quantity == 9   # was 10, bought 1
    assert inv2.quantity == 3   # was 5, bought 2


async def test_checkout_clears_cart(client: AsyncClient):
    await client.post("/orders/checkout", json=SHIPPING, headers=HEADERS)
    db = CartSession()
    cart = db.query(MirrorCart).filter_by(session_token=TOKEN).first()
    items = cart.items if cart else []
    db.close()
    assert len(items) == 0


async def test_checkout_empty_cart(client: AsyncClient):
    r = await client.post("/orders/checkout", json=SHIPPING, headers=OTHER_HEADERS)
    assert r.status_code == 400
    assert "empty" in r.json()["detail"].lower()


async def test_checkout_insufficient_stock(client: AsyncClient):
    # Drain stock for product 2 so quantity=2 exceeds available=1
    db = AdminSession()
    inv = db.query(MirrorInventory).filter_by(product_id=2).first()
    inv.quantity = 1
    db.commit()
    db.close()

    r = await client.post("/orders/checkout", json=SHIPPING, headers=HEADERS)
    assert r.status_code == 409
    assert "Python Book" in r.json()["detail"]


async def test_checkout_missing_token(client: AsyncClient):
    r = await client.post("/orders/checkout", json=SHIPPING)
    assert r.status_code == 422


async def test_checkout_missing_fields(client: AsyncClient):
    r = await client.post("/orders/checkout", json={"shipping_name": "Jane"}, headers=HEADERS)
    assert r.status_code == 422


async def test_checkout_empty_shipping_name(client: AsyncClient):
    bad = {**SHIPPING, "shipping_name": "   "}
    r = await client.post("/orders/checkout", json=bad, headers=HEADERS)
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Order retrieval
# ---------------------------------------------------------------------------


async def test_list_orders_empty(client: AsyncClient):
    r = await client.get("/orders", headers=OTHER_HEADERS)
    assert r.status_code == 200
    assert r.json() == []


async def test_list_orders_after_checkout(client: AsyncClient):
    await client.post("/orders/checkout", json=SHIPPING, headers=HEADERS)
    r = await client.get("/orders", headers=HEADERS)
    assert r.status_code == 200
    assert len(r.json()) == 1


async def test_get_order_detail(client: AsyncClient):
    created = (await client.post("/orders/checkout", json=SHIPPING, headers=HEADERS)).json()
    r = await client.get(f"/orders/{created['id']}", headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]


async def test_get_order_not_found(client: AsyncClient):
    r = await client.get("/orders/9999", headers=HEADERS)
    assert r.status_code == 404


async def test_order_isolation_between_sessions(client: AsyncClient):
    """Orders from one session are not visible to another."""
    await client.post("/orders/checkout", json=SHIPPING, headers=HEADERS)
    r = await client.get("/orders", headers=OTHER_HEADERS)
    assert r.json() == []


async def test_multiple_orders_same_session(client: AsyncClient):
    """Place two orders from the same session token sequentially."""
    # First checkout
    await client.post("/orders/checkout", json=SHIPPING, headers=HEADERS)

    # Re-seed cart for second checkout
    db = CartSession()
    cart = db.query(MirrorCart).filter_by(session_token=TOKEN).first()
    if not cart:
        cart = MirrorCart(session_token=TOKEN)
        db.add(cart)
        db.flush()
    db.add(MirrorCartItem(
        cart_id=cart.id,
        product_id=1,
        unit_price=999.99,
        product_name="Laptop Pro",
        product_sku="LAP-001",
        primary_image_url=None,
        quantity=1,
    ))
    db.commit()
    db.close()

    await client.post("/orders/checkout", json=SHIPPING, headers=HEADERS)

    r = await client.get("/orders", headers=HEADERS)
    assert len(r.json()) == 2
