"""
Read/write ORM mirror of the admin DB inventory table.
Uses a separate DeclarativeBase so these tables are NOT created in orders.db.
"""
from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class AdminMirrorBase(DeclarativeBase):
    pass


class MirrorInventory(AdminMirrorBase):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
