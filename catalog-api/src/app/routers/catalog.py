import math
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database import get_db
from app.helpers import to_autocomplete, to_detail, to_summary
from app.models.category import Category
from app.models.product import Product, ProductStatus
from app.schemas.catalog import (
    AutocompleteResult,
    CategoryOut,
    ProductDetail,
    ProductPage,
    ProductSummary,
)

router = APIRouter(prefix="/catalog", tags=["catalog"])

SortField = Literal["price_asc", "price_desc", "name_asc", "newest"]

_SORT_MAP = {
    "price_asc": Product.price.asc(),
    "price_desc": Product.price.desc(),
    "name_asc": Product.name.asc(),
    "newest": Product.id.desc(),
}


def _active_products(db: Session):
    return (
        db.query(Product)
        .options(
            joinedload(Product.images),
            joinedload(Product.inventory),
            joinedload(Product.category),
        )
        .filter(Product.status == ProductStatus.active)
    )


# ─── Categories ───────────────────────────────────────────────────────────────

@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name).all()


# ─── Featured ─────────────────────────────────────────────────────────────────

@router.get("/products/featured", response_model=list[ProductSummary])
def featured_products(limit: int = 8, db: Session = Depends(get_db)):
    products = (
        _active_products(db)
        .filter(Product.is_featured == True)  # noqa: E712
        .limit(limit)
        .all()
    )
    return [to_summary(p) for p in products]


# ─── Autocomplete ─────────────────────────────────────────────────────────────

@router.get("/products/autocomplete", response_model=list[AutocompleteResult])
def autocomplete(q: str, limit: int = 5, db: Session = Depends(get_db)):
    if len(q) < 2:
        return []
    products = (
        _active_products(db)
        .filter(Product.name.ilike(f"%{q}%"))
        .limit(limit)
        .all()
    )
    return [to_autocomplete(p) for p in products]


# ─── Products list / search ────────────────────────────────────────────────────

@router.get("/products", response_model=ProductPage)
def list_products(
    q: str | None = None,
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock: bool | None = None,
    sort: SortField = "newest",
    page: int = 1,
    page_size: int = settings.default_page_size,
    db: Session = Depends(get_db),
):
    query = _active_products(db)

    if q:
        query = query.filter(
            or_(Product.name.ilike(f"%{q}%"), Product.description.ilike(f"%{q}%"))
        )
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # in_stock filter: join inventory
    if in_stock:
        from app.models.inventory import Inventory

        query = query.join(Inventory, Inventory.product_id == Product.id).filter(
            Inventory.quantity > 0
        )

    total = query.with_entities(func.count(Product.id)).scalar() or 0

    order_clause = _SORT_MAP.get(sort, Product.id.desc())
    products = query.order_by(order_clause).offset((page - 1) * page_size).limit(page_size).all()

    return ProductPage(
        items=[to_summary(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
        pages=max(1, math.ceil(total / page_size)),
    )


# ─── Product detail ───────────────────────────────────────────────────────────

@router.get("/products/{product_id}", response_model=ProductDetail)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .options(
            joinedload(Product.images),
            joinedload(Product.inventory),
            joinedload(Product.category),
        )
        .filter(Product.id == product_id, Product.status == ProductStatus.active)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return to_detail(product)


# ─── Related products ─────────────────────────────────────────────────────────

@router.get("/products/{product_id}/related", response_model=list[ProductSummary])
def related_products(product_id: int, limit: int = 4, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.status == ProductStatus.active)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.category_id is None:
        return []

    related = (
        _active_products(db)
        .filter(Product.category_id == product.category_id, Product.id != product_id)
        .limit(limit)
        .all()
    )
    return [to_summary(p) for p in related]
