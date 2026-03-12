import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProductStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus), default=ProductStatus.active, nullable=False
    )
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    category: Mapped["Category"] = relationship("Category", back_populates="products")  # noqa: F821
    images: Mapped[list["ProductImage"]] = relationship(  # noqa: F821
        "ProductImage", back_populates="product", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[list["ProductAuditLog"]] = relationship(  # noqa: F821
        "ProductAuditLog", back_populates="product", cascade="all, delete-orphan"
    )
    inventory: Mapped["Inventory"] = relationship(  # noqa: F821
        "Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan"
    )
