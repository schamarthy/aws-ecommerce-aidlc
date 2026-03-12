from datetime import datetime

from pydantic import BaseModel, field_validator


class CartItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_sku: str
    primary_image_url: str | None
    unit_price: float
    quantity: int
    line_total: float
    added_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_item(cls, item: object) -> "CartItemOut":
        from app.models.cart import CartItem
        i: CartItem = item  # type: ignore
        return cls(
            id=i.id,
            product_id=i.product_id,
            product_name=i.product_name,
            product_sku=i.product_sku,
            primary_image_url=i.primary_image_url,
            unit_price=float(i.unit_price),
            quantity=i.quantity,
            line_total=float(i.unit_price) * i.quantity,
            added_at=i.added_at,
        )


class CartOut(BaseModel):
    id: int
    session_token: str
    items: list[CartItemOut]
    subtotal: float
    item_count: int

    @classmethod
    def from_orm_cart(cls, cart: object) -> "CartOut":
        from app.models.cart import Cart
        c: Cart = cart  # type: ignore
        items = [CartItemOut.from_orm_item(i) for i in c.items]
        subtotal = sum(i.line_total for i in items)
        item_count = sum(i.quantity for i in items)
        return cls(
            id=c.id,
            session_token=c.session_token,
            items=items,
            subtotal=round(subtotal, 2),
            item_count=item_count,
        )


class AddItemRequest(BaseModel):
    product_id: int
    quantity: int = 1

    @field_validator("quantity")
    @classmethod
    def qty_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("quantity must be at least 1")
        return v


class UpdateItemRequest(BaseModel):
    quantity: int

    @field_validator("quantity")
    @classmethod
    def qty_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("quantity must be at least 1")
        return v
