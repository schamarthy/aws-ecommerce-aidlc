from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

from app.models.order import OrderStatus


class CheckoutRequest(BaseModel):
    shipping_name: str
    shipping_email: str
    shipping_address: str

    @field_validator("shipping_name", "shipping_email", "shipping_address")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_sku: str
    primary_image_url: str | None
    unit_price: float
    quantity: int
    line_total: float

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_item(cls, item: object) -> "OrderItemOut":
        from app.models.order import OrderItem
        i: OrderItem = item  # type: ignore
        return cls(
            id=i.id,
            product_id=i.product_id,
            product_name=i.product_name,
            product_sku=i.product_sku,
            primary_image_url=i.primary_image_url,
            unit_price=float(i.unit_price),
            quantity=i.quantity,
            line_total=float(i.line_total),
        )


class OrderOut(BaseModel):
    id: int
    session_token: str
    status: OrderStatus
    shipping_name: str
    shipping_email: str
    shipping_address: str
    total_amount: float
    created_at: datetime
    items: list[OrderItemOut]

    @classmethod
    def from_orm_order(cls, order: object) -> "OrderOut":
        from app.models.order import Order
        o: Order = order  # type: ignore
        return cls(
            id=o.id,
            session_token=o.session_token,
            status=o.status,
            shipping_name=o.shipping_name,
            shipping_email=o.shipping_email,
            shipping_address=o.shipping_address,
            total_amount=float(o.total_amount),
            created_at=o.created_at,
            items=[OrderItemOut.from_orm_item(i) for i in o.items],
        )
