import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import admin-api models to create the shared schema
import sys
import os

# We re-use catalog-api's own model definitions (same table names)
from app.database import Base, get_db
from app.main import app
from app.models.category import Category
from app.models.inventory import Inventory
from app.models.product import Product, ProductStatus
from app.models.product_image import ProductImage

TEST_DB_URL = "sqlite:///./test_catalog.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    _seed(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def _seed(db):
    cat1 = Category(id=1, name="Electronics", description="Gadgets")
    cat2 = Category(id=2, name="Books", description="Reading")
    db.add_all([cat1, cat2])
    db.flush()

    p1 = Product(
        id=1, name="Laptop Pro", price=999.99, sku="LAP-001",
        status=ProductStatus.active, is_featured=True, category_id=1,
    )
    p2 = Product(
        id=2, name="Python Book", price=39.99, sku="BK-001",
        status=ProductStatus.active, is_featured=False, category_id=2,
    )
    p3 = Product(
        id=3, name="Widget", price=9.99, sku="WID-001",
        status=ProductStatus.inactive, is_featured=False, category_id=1,
    )
    p4 = Product(
        id=4, name="Headphones", price=149.99, sku="HEAD-001",
        status=ProductStatus.active, is_featured=True, category_id=1,
    )
    db.add_all([p1, p2, p3, p4])
    db.flush()

    img = ProductImage(id=1, product_id=1, storage_url="/uploads/1/img.jpg", is_primary=True, display_order=0)
    db.add(img)
    db.flush()

    inv1 = Inventory(product_id=1, quantity=50, low_stock_threshold=10)
    inv2 = Inventory(product_id=2, quantity=3, low_stock_threshold=5)
    inv3 = Inventory(product_id=4, quantity=0, low_stock_threshold=5)
    db.add_all([inv1, inv2, inv3])
    db.commit()


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
