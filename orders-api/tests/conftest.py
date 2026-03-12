import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_admin_db, get_cart_db, get_db
from app.main import app
from app.models.admin_mirror import AdminMirrorBase, MirrorInventory
from app.models.cart_mirror import CartMirrorBase, MirrorCart, MirrorCartItem

ORDERS_DB_URL = "sqlite:///./test_orders.db"
CART_DB_URL = "sqlite:///./test_cart_mirror.db"
ADMIN_DB_URL = "sqlite:///./test_admin_mirror.db"

orders_engine = create_engine(ORDERS_DB_URL, connect_args={"check_same_thread": False})
cart_engine = create_engine(CART_DB_URL, connect_args={"check_same_thread": False})
admin_engine = create_engine(ADMIN_DB_URL, connect_args={"check_same_thread": False})

OrdersSession = sessionmaker(autocommit=False, autoflush=False, bind=orders_engine)
CartSession = sessionmaker(autocommit=False, autoflush=False, bind=cart_engine)
AdminSession = sessionmaker(autocommit=False, autoflush=False, bind=admin_engine)

TOKEN = "test-session-token-abc123"
HEADERS = {"X-Session-Token": TOKEN}


@pytest.fixture(autouse=True)
def setup_dbs():
    Base.metadata.create_all(bind=orders_engine)
    CartMirrorBase.metadata.create_all(bind=cart_engine)
    AdminMirrorBase.metadata.create_all(bind=admin_engine)
    _seed_cart()
    _seed_admin()
    yield
    Base.metadata.drop_all(bind=orders_engine)
    CartMirrorBase.metadata.drop_all(bind=cart_engine)
    AdminMirrorBase.metadata.drop_all(bind=admin_engine)


def _seed_cart():
    """Seed cart DB with a cart for TOKEN containing 2 items."""
    db = CartSession()
    cart = MirrorCart(session_token=TOKEN)
    db.add(cart)
    db.flush()
    db.add(MirrorCartItem(
        cart_id=cart.id,
        product_id=1,
        unit_price=999.99,
        product_name="Laptop Pro",
        product_sku="LAP-001",
        primary_image_url="/uploads/1/img.jpg",
        quantity=1,
    ))
    db.add(MirrorCartItem(
        cart_id=cart.id,
        product_id=2,
        unit_price=39.99,
        product_name="Python Book",
        product_sku="BK-001",
        primary_image_url=None,
        quantity=2,
    ))
    db.commit()
    db.close()


def _seed_admin():
    """Seed admin DB with inventory for products used in tests."""
    db = AdminSession()
    db.add(MirrorInventory(product_id=1, quantity=10))
    db.add(MirrorInventory(product_id=2, quantity=5))
    db.commit()
    db.close()


def override_get_db():
    db = OrdersSession()
    try:
        yield db
    finally:
        db.close()


def override_get_cart_db():
    db = CartSession()
    try:
        yield db
    finally:
        db.close()


def override_get_admin_db():
    db = AdminSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_cart_db] = override_get_cart_db
app.dependency_overrides[get_admin_db] = override_get_admin_db


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
