"""
Read-only ORM mirrors of the admin DB tables.
Uses a separate DeclarativeBase so these tables are NOT created in cart.db.
"""
import enum

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class CatalogBase(DeclarativeBase):
    pass


class ProductStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"


class CatalogProduct(CatalogBase):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    sku: Mapped[str] = mapped_column(String(100))
    status: Mapped[ProductStatus] = mapped_column(Enum(ProductStatus))
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)

    images: Mapped[list["CatalogImage"]] = relationship("CatalogImage", back_populates="product")
    inventory: Mapped["CatalogInventory"] = relationship(
        "CatalogInventory", back_populates="product", uselist=False
    )


class CatalogImage(CatalogBase):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    storage_url: Mapped[str] = mapped_column(String(500))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped["CatalogProduct"] = relationship("CatalogProduct", back_populates="images")


class CatalogInventory(CatalogBase):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), unique=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped["CatalogProduct"] = relationship("CatalogProduct", back_populates="inventory")
