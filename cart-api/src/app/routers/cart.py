from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_catalog_db, get_db
from app.schemas.cart import AddItemRequest, CartOut, UpdateItemRequest
from app.services.cart_service import (
    add_item,
    clear_cart,
    get_or_create_cart,
    remove_item,
    update_item,
)

router = APIRouter(prefix="/cart", tags=["cart"])


def _require_token(x_session_token: str = Header(..., alias="X-Session-Token")) -> str:
    if not x_session_token or len(x_session_token) < 8:
        raise HTTPException(status_code=400, detail="Valid X-Session-Token header required")
    return x_session_token


@router.get("", response_model=CartOut)
def get_cart(
    token: str = Depends(_require_token),
    db: Session = Depends(get_db),
):
    cart = get_or_create_cart(db, token)
    return CartOut.from_orm_cart(cart)


@router.post("/items", response_model=CartOut, status_code=201)
def add_to_cart(
    body: AddItemRequest,
    token: str = Depends(_require_token),
    db: Session = Depends(get_db),
    catalog_db: Session = Depends(get_catalog_db),
):
    cart = add_item(db, catalog_db, token, body.product_id, body.quantity)
    return CartOut.from_orm_cart(cart)


@router.patch("/items/{item_id}", response_model=CartOut)
def update_cart_item(
    item_id: int,
    body: UpdateItemRequest,
    token: str = Depends(_require_token),
    db: Session = Depends(get_db),
    catalog_db: Session = Depends(get_catalog_db),
):
    cart = update_item(db, catalog_db, token, item_id, body.quantity)
    return CartOut.from_orm_cart(cart)


@router.delete("/items/{item_id}", response_model=CartOut)
def remove_from_cart(
    item_id: int,
    token: str = Depends(_require_token),
    db: Session = Depends(get_db),
):
    cart = remove_item(db, token, item_id)
    return CartOut.from_orm_cart(cart)


@router.delete("", response_model=CartOut)
def empty_cart(
    token: str = Depends(_require_token),
    db: Session = Depends(get_db),
):
    cart = clear_cart(db, token)
    return CartOut.from_orm_cart(cart)
