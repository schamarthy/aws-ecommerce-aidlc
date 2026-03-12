import pytest


# ─── Categories ────────────────────────────────────────────────────────────────

async def test_list_categories(client):
    resp = await client.get("/catalog/categories")
    assert resp.status_code == 200
    names = [c["name"] for c in resp.json()]
    assert "Electronics" in names
    assert "Books" in names


# ─── Featured ─────────────────────────────────────────────────────────────────

async def test_featured_products(client):
    resp = await client.get("/catalog/products/featured")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert all(p["is_featured"] for p in data)
    # inactive product must not appear
    names = [p["name"] for p in data]
    assert "Widget" not in names


# ─── Product list ─────────────────────────────────────────────────────────────

async def test_list_products_active_only(client):
    resp = await client.get("/catalog/products")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3  # p1, p2, p4 (p3 is inactive)
    names = [p["name"] for p in data["items"]]
    assert "Widget" not in names


async def test_filter_by_category(client):
    resp = await client.get("/catalog/products?category_id=1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2  # Laptop Pro + Headphones (Widget inactive)


async def test_filter_min_price(client):
    resp = await client.get("/catalog/products?min_price=100")
    assert resp.status_code == 200
    names = [p["name"] for p in resp.json()["items"]]
    assert "Laptop Pro" in names
    assert "Headphones" in names
    assert "Python Book" not in names


async def test_sort_price_asc(client):
    resp = await client.get("/catalog/products?sort=price_asc")
    assert resp.status_code == 200
    prices = [p["price"] for p in resp.json()["items"]]
    assert prices == sorted(prices)


async def test_search_keyword(client):
    resp = await client.get("/catalog/products?q=laptop")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Laptop Pro"


async def test_pagination(client):
    resp = await client.get("/catalog/products?page=1&page_size=2")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["pages"] == 2


# ─── Autocomplete ─────────────────────────────────────────────────────────────

async def test_autocomplete(client):
    resp = await client.get("/catalog/products/autocomplete?q=lap")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Laptop Pro"


async def test_autocomplete_too_short(client):
    resp = await client.get("/catalog/products/autocomplete?q=l")
    assert resp.status_code == 200
    assert resp.json() == []


# ─── Product detail ───────────────────────────────────────────────────────────

async def test_product_detail(client):
    resp = await client.get("/catalog/products/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Laptop Pro"
    assert data["stock_status"] == "in_stock"
    assert data["quantity"] == 50
    assert len(data["images"]) == 1
    assert data["category"]["name"] == "Electronics"


async def test_product_detail_inactive_returns_404(client):
    resp = await client.get("/catalog/products/3")
    assert resp.status_code == 404


async def test_product_detail_low_stock(client):
    resp = await client.get("/catalog/products/2")
    assert resp.status_code == 200
    assert resp.json()["stock_status"] == "low_stock"


async def test_product_detail_out_of_stock(client):
    resp = await client.get("/catalog/products/4")
    assert resp.status_code == 200
    assert resp.json()["stock_status"] == "out_of_stock"


# ─── Related products ─────────────────────────────────────────────────────────

async def test_related_products(client):
    # Laptop Pro (cat 1) should return Headphones (cat 1, also active)
    resp = await client.get("/catalog/products/1/related")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Headphones"


async def test_related_products_no_category(client):
    # Python Book is in cat 2 (alone), should return empty
    resp = await client.get("/catalog/products/2/related")
    assert resp.status_code == 200
    assert resp.json() == []


# ─── In-stock filter ──────────────────────────────────────────────────────────

async def test_in_stock_filter(client):
    resp = await client.get("/catalog/products?in_stock=true")
    assert resp.status_code == 200
    data = resp.json()
    # p4 (Headphones) has qty=0, so should not appear
    names = [p["name"] for p in data["items"]]
    assert "Headphones" not in names
    assert "Laptop Pro" in names
