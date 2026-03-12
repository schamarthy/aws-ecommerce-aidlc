from datetime import datetime

from pydantic import BaseModel, field_validator


class InventoryOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    low_stock_threshold: int
    updated_at: datetime

    model_config = {"from_attributes": True}


class InventoryUpdate(BaseModel):
    quantity: int
    actor: str = "system"
    reason: str | None = None

    @field_validator("quantity")
    @classmethod
    def quantity_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("quantity must be non-negative")
        return v


class ThresholdUpdate(BaseModel):
    low_stock_threshold: int

    @field_validator("low_stock_threshold")
    @classmethod
    def threshold_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("threshold must be non-negative")
        return v


class BulkUpdateItem(BaseModel):
    product_id: int
    quantity: int
    actor: str = "system"
    reason: str | None = None


class BulkUpdateRequest(BaseModel):
    updates: list[BulkUpdateItem]


class StockAuditOut(BaseModel):
    id: int
    product_id: int
    inventory_id: int
    previous_quantity: int
    new_quantity: int
    adjustment: int
    actor: str
    reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class InventoryDashboardItem(BaseModel):
    product_id: int
    product_name: str
    sku: str
    quantity: int
    low_stock_threshold: int
    is_low_stock: bool

    model_config = {"from_attributes": True}
