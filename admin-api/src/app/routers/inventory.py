from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.stock_audit_log import StockAuditLog
from app.schemas.inventory import (
    BulkUpdateRequest,
    InventoryDashboardItem,
    InventoryOut,
    InventoryUpdate,
    StockAuditOut,
    ThresholdUpdate,
)
from app.services.inventory_service import get_or_create_inventory, update_stock

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("", response_model=list[InventoryDashboardItem])
def inventory_dashboard(db: Session = Depends(get_db)):
    rows = (
        db.query(Inventory, Product)
        .join(Product, Product.id == Inventory.product_id)
        .all()
    )
    result = []
    for inv, prod in rows:
        result.append(
            InventoryDashboardItem(
                product_id=inv.product_id,
                product_name=prod.name,
                sku=prod.sku,
                quantity=inv.quantity,
                low_stock_threshold=inv.low_stock_threshold,
                is_low_stock=inv.quantity <= inv.low_stock_threshold,
            )
        )
    return result


@router.get("/{product_id}", response_model=InventoryOut)
def get_inventory(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return get_or_create_inventory(db, product_id)


@router.put("/{product_id}", response_model=InventoryOut)
def update_inventory(product_id: int, data: InventoryUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    inv = get_or_create_inventory(db, product_id)
    return update_stock(db, inv, data.quantity, data.actor, data.reason)


@router.patch("/{product_id}/threshold", response_model=InventoryOut)
def update_threshold(product_id: int, data: ThresholdUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    inv = get_or_create_inventory(db, product_id)
    inv.low_stock_threshold = data.low_stock_threshold
    db.commit()
    db.refresh(inv)
    return inv


@router.get("/{product_id}/history", response_model=list[StockAuditOut])
def stock_history(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return (
        db.query(StockAuditLog)
        .filter(StockAuditLog.product_id == product_id)
        .order_by(StockAuditLog.created_at.desc())
        .all()
    )


@router.post("/bulk-update", response_model=list[InventoryOut])
def bulk_update(data: BulkUpdateRequest, db: Session = Depends(get_db)):
    results = []
    for item in data.updates:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=404, detail=f"Product {item.product_id} not found"
            )
        inv = get_or_create_inventory(db, item.product_id)
        inv = update_stock(db, inv, item.quantity, item.actor, item.reason)
        results.append(inv)
    return results
