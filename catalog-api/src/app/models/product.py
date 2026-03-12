import enum

from sqlalchemy import Boolean, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProductStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    sku: Mapped[str] = mapped_column(String(100))
    status: Mapped[ProductStatus] = mapped_column(Enum(ProductStatus))
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)

    category: Mapped["Category"] = relationship("Category", back_populates="products")  # noqa: F821
    images: Mapped[list["ProductImage"]] = relationship("ProductImage", back_populates="product")  # noqa: F821
    inventory: Mapped["Inventory"] = relationship("Inventory", back_populates="product", uselist=False)  # noqa: F821
