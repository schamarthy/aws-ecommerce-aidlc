"""
Read/write ORM mirrors of the cart DB tables.
Uses a separate DeclarativeBase so these tables are NOT created in orders.db.
"""
from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class CartMirrorBase(DeclarativeBase):
    pass


class MirrorCart(CartMirrorBase):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_token: Mapped[str] = mapped_column(String(64))

    items: Mapped[list["MirrorCartItem"]] = relationship(
        "MirrorCartItem", back_populates="cart", cascade="all, delete-orphan"
    )


class MirrorCartItem(CartMirrorBase):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_sku: Mapped[str] = mapped_column(String(100), nullable=False)
    primary_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    cart: Mapped["MirrorCart"] = relationship("MirrorCart", back_populates="items")
