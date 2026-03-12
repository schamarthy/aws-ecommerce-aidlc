from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# Orders own database
orders_engine = create_engine(
    settings.orders_database_url,
    connect_args={"check_same_thread": False},
)
OrdersSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=orders_engine)

# Cart DB — read cart items and clear cart on checkout
cart_engine = create_engine(
    settings.cart_database_url,
    connect_args={"check_same_thread": False},
)
CartSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cart_engine)

# Admin DB — read and deduct inventory on checkout
admin_engine = create_engine(
    settings.admin_database_url,
    connect_args={"check_same_thread": False},
)
AdminSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=admin_engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = OrdersSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_cart_db():
    db = CartSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_admin_db():
    db = AdminSessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=orders_engine)
