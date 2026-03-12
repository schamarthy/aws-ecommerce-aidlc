from datetime import datetime

from pydantic import BaseModel, field_validator

from app.models.product import ProductStatus
from app.schemas.image import ImageOut


class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    sku: str
    status: ProductStatus = ProductStatus.active
    is_featured: bool = False
    category_id: int | None = None
    created_by: str | None = None
    updated_by: str | None = None

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError("price must be non-negative")
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    sku: str | None = None
    status: ProductStatus | None = None
    is_featured: bool | None = None
    category_id: int | None = None
    updated_by: str | None = None


class ProductStatusUpdate(BaseModel):
    status: ProductStatus


class ProductFeaturedUpdate(BaseModel):
    is_featured: bool


class ProductOut(ProductBase):
    id: int
    images: list[ImageOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductAuditOut(BaseModel):
    id: int
    product_id: int
    field_name: str
    previous_value: str | None
    new_value: str | None
    actor: str
    changed_at: datetime

    model_config = {"from_attributes": True}
