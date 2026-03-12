from pydantic import BaseModel, computed_field


class ImageOut(BaseModel):
    id: int
    storage_url: str
    is_primary: bool
    display_order: int

    model_config = {"from_attributes": True}


class CategoryOut(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = {"from_attributes": True}


class StockStatus(str):
    pass


class ProductSummary(BaseModel):
    id: int
    name: str
    price: float
    sku: str
    is_featured: bool
    category_id: int | None = None
    primary_image_url: str | None = None
    stock_status: str  # "in_stock" | "low_stock" | "out_of_stock"

    model_config = {"from_attributes": True}


class ProductDetail(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    sku: str
    is_featured: bool
    category_id: int | None = None
    category: CategoryOut | None = None
    images: list[ImageOut] = []
    stock_status: str
    quantity: int

    model_config = {"from_attributes": True}


class ProductPage(BaseModel):
    items: list[ProductSummary]
    total: int
    page: int
    page_size: int
    pages: int


class AutocompleteResult(BaseModel):
    id: int
    name: str
    primary_image_url: str | None = None
