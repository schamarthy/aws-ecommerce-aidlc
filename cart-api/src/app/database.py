from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# Cart's own database
cart_engine = create_engine(
    settings.cart_database_url,
    connect_args={"check_same_thread": False},
)
CartSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cart_engine)

# Read-only connection to the shared admin/catalog DB
catalog_engine = create_engine(
    settings.catalog_database_url,
    connect_args={"check_same_thread": False},
)
CatalogSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=catalog_engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = CartSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_catalog_db():
    db = CatalogSessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=cart_engine)
