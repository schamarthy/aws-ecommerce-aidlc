from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.admin_mirror import MirrorInventory
from app.models.cart_mirror import MirrorCart
from app.models.order import Order, OrderItem, OrderStatus


def checkout(
    db: Session,
    cart_db: Session,
    admin_db: Session,
    session_token: str,
    shipping_name: str,
    shipping_email: str,
    shipping_address: str,
) -> Order:
    # 1. Load cart
    cart = (
        cart_db.query(MirrorCart)
        .options(joinedload(MirrorCart.items))
        .filter(MirrorCart.session_token == session_token)
        .first()
    )
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # 2. Validate stock for all items before making any changes
    stock_map: dict[int, MirrorInventory] = {}
    for ci in cart.items:
        inv = admin_db.query(MirrorInventory).filter(MirrorInventory.product_id == ci.product_id).first()
        available = inv.quantity if inv else 0
        if available < ci.quantity:
            raise HTTPException(
                status_code=409,
                detail=f"'{ci.product_name}': only {available} unit(s) in stock",
            )
        stock_map[ci.product_id] = inv  # type: ignore

    # 3. Create order record
    total = round(sum(float(ci.unit_price) * ci.quantity for ci in cart.items), 2)
    order = Order(
        session_token=session_token,
        status=OrderStatus.confirmed,
        shipping_name=shipping_name,
        shipping_email=shipping_email,
        shipping_address=shipping_address,
        total_amount=total,
    )
    db.add(order)
    db.flush()  # get order.id before adding items

    # 4. Create order items (price snapshot from cart)
    for ci in cart.items:
        line_total = round(float(ci.unit_price) * ci.quantity, 2)
        db.add(OrderItem(
            order_id=order.id,
            product_id=ci.product_id,
            product_name=ci.product_name,
            product_sku=ci.product_sku,
            primary_image_url=ci.primary_image_url,
            unit_price=float(ci.unit_price),
            quantity=ci.quantity,
            line_total=line_total,
        ))

    # 5. Deduct inventory
    for ci in cart.items:
        stock_map[ci.product_id].quantity -= ci.quantity
    admin_db.commit()

    # 6. Clear cart
    for item in list(cart.items):
        cart_db.delete(item)
    cart_db.commit()

    db.commit()
    # Reload with items
    return (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.id == order.id)
        .first()  # type: ignore
    )


def get_orders(db: Session, session_token: str) -> list[Order]:
    return (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.session_token == session_token)
        .order_by(Order.created_at.desc())
        .all()
    )


def get_order(db: Session, session_token: str, order_id: int) -> Order:
    order = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.id == order_id, Order.session_token == session_token)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
