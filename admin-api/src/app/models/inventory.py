from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (CheckConstraint("quantity >= 0", name="ck_inventory_quantity_non_negative"),)

    product: Mapped["Product"] = relationship("Product", back_populates="inventory")  # noqa: F821
    stock_audit_logs: Mapped[list["StockAuditLog"]] = relationship(  # noqa: F821
        "StockAuditLog", back_populates="inventory", cascade="all, delete-orphan"
    )
