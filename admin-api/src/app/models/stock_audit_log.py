from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StockAuditLog(Base):
    __tablename__ = "stock_audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    inventory_id: Mapped[int] = mapped_column(
        ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False
    )
    previous_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    new_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    adjustment: Mapped[int] = mapped_column(Integer, nullable=False)  # computed: new - previous
    actor: Mapped[str] = mapped_column(String(255), default="system", nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    inventory: Mapped["Inventory"] = relationship("Inventory", back_populates="stock_audit_logs")  # noqa: F821
