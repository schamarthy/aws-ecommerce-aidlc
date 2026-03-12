from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.stock_audit_log import StockAuditLog


def get_or_create_inventory(db: Session, product_id: int) -> Inventory:
    inv = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inv:
        inv = Inventory(product_id=product_id, quantity=0)
        db.add(inv)
        db.commit()
        db.refresh(inv)
    return inv


def update_stock(
    db: Session,
    inventory: Inventory,
    new_quantity: int,
    actor: str = "system",
    reason: str | None = None,
) -> Inventory:
    previous = inventory.quantity
    log = StockAuditLog(
        product_id=inventory.product_id,
        inventory_id=inventory.id,
        previous_quantity=previous,
        new_quantity=new_quantity,
        adjustment=new_quantity - previous,
        actor=actor,
        reason=reason,
    )
    inventory.quantity = new_quantity
    db.add(log)
    db.commit()
    db.refresh(inventory)
    return inventory
