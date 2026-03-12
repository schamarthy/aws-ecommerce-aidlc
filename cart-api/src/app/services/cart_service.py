from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload as _joinedload

from app.models.cart import Cart, CartItem
from app.models.catalog_mirror import CatalogInventory, CatalogProduct, ProductStatus


def get_or_create_cart(db: Session, session_token: str) -> Cart:
    cart = (
        db.query(Cart)
        .options(_joinedload(Cart.items))
        .filter(Cart.session_token == session_token)
        .first()
    )
    if not cart:
        cart = Cart(session_token=session_token)
        db.add(cart)
        db.commit()
        db.refresh(cart)
        cart = (
            db.query(Cart)
            .options(_joinedload(Cart.items))
            .filter(Cart.session_token == session_token)
            .first()
        )
    return cart  # type: ignore


def _get_product_or_404(catalog_db: Session, product_id: int) -> CatalogProduct:
    product = (
        catalog_db.query(CatalogProduct)
        .options(
            _joinedload(CatalogProduct.images),
            _joinedload(CatalogProduct.inventory),
        )
        .filter(
            CatalogProduct.id == product_id,
            CatalogProduct.status == ProductStatus.active,
        )
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or not available")
    return product


def _available_stock(product: CatalogProduct) -> int:
    if product.inventory is None:
        return 0
    return product.inventory.quantity


def _primary_image(product: CatalogProduct) -> str | None:
    primary = next((img for img in product.images if img.is_primary), None)
    if primary is None and product.images:
        primary = sorted(product.images, key=lambda i: i.display_order)[0]
    return primary.storage_url if primary else None


def add_item(
    db: Session,
    catalog_db: Session,
    session_token: str,
    product_id: int,
    quantity: int,
) -> Cart:
    product = _get_product_or_404(catalog_db, product_id)
    stock = _available_stock(product)

    cart = get_or_create_cart(db, session_token)

    # Check if already in cart
    existing = next((i for i in cart.items if i.product_id == product_id), None)
    new_qty = (existing.quantity if existing else 0) + quantity

    if new_qty > stock:
        raise HTTPException(
            status_code=409,
            detail=f"Only {stock} unit(s) available (currently {existing.quantity if existing else 0} in cart)",
        )

    if existing:
        existing.quantity = new_qty
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            unit_price=float(product.price),
            product_name=product.name,
            product_sku=product.sku,
            primary_image_url=_primary_image(product),
            quantity=quantity,
        )
        db.add(item)

    db.commit()
    return get_or_create_cart(db, session_token)


def update_item(
    db: Session,
    catalog_db: Session,
    session_token: str,
    item_id: int,
    quantity: int,
) -> Cart:
    cart = get_or_create_cart(db, session_token)
    item = next((i for i in cart.items if i.id == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    product = _get_product_or_404(catalog_db, item.product_id)
    stock = _available_stock(product)

    if quantity > stock:
        raise HTTPException(status_code=409, detail=f"Only {stock} unit(s) available")

    item.quantity = quantity
    db.commit()
    return get_or_create_cart(db, session_token)


def remove_item(db: Session, session_token: str, item_id: int) -> Cart:
    cart = get_or_create_cart(db, session_token)
    item = next((i for i in cart.items if i.id == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(item)
    db.commit()
    return get_or_create_cart(db, session_token)


def clear_cart(db: Session, session_token: str) -> Cart:
    cart = get_or_create_cart(db, session_token)
    for item in list(cart.items):
        db.delete(item)
    db.commit()
    return get_or_create_cart(db, session_token)
