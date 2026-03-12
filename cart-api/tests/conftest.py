import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_catalog_db, get_db
from app.main import app
from app.models.catalog_mirror import (
    CatalogBase,
    CatalogImage,
    CatalogInventory,
    CatalogProduct,
    ProductStatus,
)

CART_DB_URL = "sqlite:///./test_cart.db"
CATALOG_DB_URL = "sqlite:///./test_catalog_mirror.db"

cart_engine = create_engine(CART_DB_URL, connect_args={"check_same_thread": False})
catalog_engine = create_engine(CATALOG_DB_URL, connect_args={"check_same_thread": False})

CartSession = sessionmaker(autocommit=False, autoflush=False, bind=cart_engine)
CatalogSession = sessionmaker(autocommit=False, autoflush=False, bind=catalog_engine)


@pytest.fixture(autouse=True)
def setup_dbs():
    Base.metadata.create_all(bind=cart_engine)
    CatalogBase.metadata.create_all(bind=catalog_engine)
    _seed_catalog()
    yield
    Base.metadata.drop_all(bind=cart_engine)
    CatalogBase.metadata.drop_all(bind=catalog_engine)


def _seed_catalog():
    db = CatalogSession()
    p1 = CatalogProduct(id=1, name="Laptop Pro", price=999.99, sku="LAP-001", status=ProductStatus.active)
    p2 = CatalogProduct(id=2, name="Python Book", price=39.99, sku="BK-001", status=ProductStatus.active)
    p3 = CatalogProduct(id=3, name="Archived", price=1.0, sku="ARC-001", status=ProductStatus.archived)
    db.add_all([p1, p2, p3])
    db.flush()
    img = CatalogImage(product_id=1, storage_url="/uploads/1/img.jpg", is_primary=True, display_order=0)
    db.add(img)
    inv1 = CatalogInventory(product_id=1, quantity=10)
    inv2 = CatalogInventory(product_id=2, quantity=2)
    db.add_all([inv1, inv2])
    db.commit()
    db.close()


def override_get_db():
    db = CartSession()
    try:
        yield db
    finally:
        db.close()


def override_get_catalog_db():
    db = CatalogSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_catalog_db] = override_get_catalog_db

TOKEN = "test-session-token-abc123"
HEADERS = {"X-Session-Token": TOKEN}


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
