from app.models.inventory import Inventory
from app.models.product import Product
from app.schemas.catalog import AutocompleteResult, ProductDetail, ProductSummary


def _stock_status(inv: Inventory | None) -> tuple[str, int]:
    if inv is None:
        return "out_of_stock", 0
    if inv.quantity <= 0:
        return "out_of_stock", inv.quantity
    if inv.quantity <= inv.low_stock_threshold:
        return "low_stock", inv.quantity
    return "in_stock", inv.quantity


def to_summary(p: Product) -> ProductSummary:
    primary = next((img for img in p.images if img.is_primary), None)
    if primary is None and p.images:
        primary = sorted(p.images, key=lambda i: i.display_order)[0]
    status, _ = _stock_status(p.inventory)
    return ProductSummary(
        id=p.id,
        name=p.name,
        price=float(p.price),
        sku=p.sku,
        is_featured=p.is_featured,
        category_id=p.category_id,
        primary_image_url=primary.storage_url if primary else None,
        stock_status=status,
    )


def to_detail(p: Product) -> ProductDetail:
    status, qty = _stock_status(p.inventory)
    return ProductDetail(
        id=p.id,
        name=p.name,
        description=p.description,
        price=float(p.price),
        sku=p.sku,
        is_featured=p.is_featured,
        category_id=p.category_id,
        category=p.category,
        images=sorted(p.images, key=lambda i: i.display_order),
        stock_status=status,
        quantity=qty,
    )


def to_autocomplete(p: Product) -> AutocompleteResult:
    primary = next((img for img in p.images if img.is_primary), None)
    if primary is None and p.images:
        primary = sorted(p.images, key=lambda i: i.display_order)[0]
    return AutocompleteResult(
        id=p.id,
        name=p.name,
        primary_image_url=primary.storage_url if primary else None,
    )
