from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.product_audit_log import ProductAuditLog
from app.schemas.product import (
    ProductAuditOut,
    ProductCreate,
    ProductFeaturedUpdate,
    ProductOut,
    ProductStatusUpdate,
    ProductUpdate,
)
from app.services.product_service import create_product, update_product

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def list_products(
    status: str | None = None,
    category_id: int | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Product)
    if status:
        q = q.filter(Product.status == status)
    if category_id:
        q = q.filter(Product.category_id == category_id)
    return q.all()


@router.post("", response_model=ProductOut, status_code=201)
def create_product_endpoint(data: ProductCreate, db: Session = Depends(get_db)):
    existing = db.query(Product).filter(Product.sku == data.sku).first()
    if existing:
        raise HTTPException(status_code=409, detail="SKU already exists")
    return create_product(db, data)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product_endpoint(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if data.sku and data.sku != product.sku:
        dup = db.query(Product).filter(Product.sku == data.sku).first()
        if dup:
            raise HTTPException(status_code=409, detail="SKU already exists")
    return update_product(db, product, data)


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()


@router.patch("/{product_id}/status", response_model=ProductOut)
def update_status(product_id: int, data: ProductStatusUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    from app.schemas.product import ProductUpdate as PU

    return update_product(db, product, PU(status=data.status))


@router.patch("/{product_id}/featured", response_model=ProductOut)
def update_featured(product_id: int, data: ProductFeaturedUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    from app.schemas.product import ProductUpdate as PU

    return update_product(db, product, PU(is_featured=data.is_featured))


@router.get("/{product_id}/audit", response_model=list[ProductAuditOut])
def get_audit_log(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return (
        db.query(ProductAuditLog)
        .filter(ProductAuditLog.product_id == product_id)
        .order_by(ProductAuditLog.changed_at.desc())
        .all()
    )
