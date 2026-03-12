from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_admin_db, get_cart_db, get_db
from app.schemas.order import CheckoutRequest, OrderOut
from app.services.order_service import checkout, get_order, get_orders

router = APIRouter(prefix="/orders", tags=["orders"])


def _require_token(x_session_token: str = Header(..., alias="X-Session-Token")) -> str:
    if not x_session_token or len(x_session_token) < 8:
        raise HTTPException(status_code=400, detail="Valid X-Session-Token header required")
    return x_session_token


@router.post("/checkout", response_model=OrderOut, status_code=201)
def place_order(
    body: CheckoutRequest,
    token: str = Depends(_require_token),
    db: Session = Depends(get_db),
    cart_db: Session = Depends(get_cart_db),
    admin_db: Session = Depends(get_admin_db),
):
    order = checkout(
        db=db,
        cart_db=cart_db,
        admin_db=admin_db,
        session_token=token,
        shipping_name=body.shipping_name,
        shipping_email=body.shipping_email,
        shipping_address=body.shipping_address,
    )
    return OrderOut.from_orm_order(order)


@router.get("", response_model=list[OrderOut])
def list_orders(
    token: str = Depends(_require_token),
    db: Session = Depends(get_db),
):
    orders = get_orders(db, token)
    return [OrderOut.from_orm_order(o) for o in orders]


@router.get("/{order_id}", response_model=OrderOut)
def get_order_detail(
    order_id: int,
    token: str = Depends(_require_token),
    db: Session = Depends(get_db),
):
    order = get_order(db, token, order_id)
    return OrderOut.from_orm_order(order)
