from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.product_audit_log import ProductAuditLog
from app.schemas.product import ProductCreate, ProductUpdate


def create_product(db: Session, data: ProductCreate) -> Product:
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, data: ProductUpdate) -> Product:
    updates = data.model_dump(exclude_unset=True)
    audit_entries = []
    for field, new_val in updates.items():
        old_val = getattr(product, field)
        if str(old_val) != str(new_val):
            audit_entries.append(
                ProductAuditLog(
                    product_id=product.id,
                    field_name=field,
                    previous_value=str(old_val) if old_val is not None else None,
                    new_value=str(new_val) if new_val is not None else None,
                    actor=data.updated_by or "system",
                )
            )
        setattr(product, field, new_val)
    db.add_all(audit_entries)
    db.commit()
    db.refresh(product)
    return product
