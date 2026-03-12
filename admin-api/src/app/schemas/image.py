from datetime import datetime

from pydantic import BaseModel


class ImageOut(BaseModel):
    id: int
    product_id: int
    storage_url: str
    is_primary: bool
    display_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ImageUpdate(BaseModel):
    is_primary: bool | None = None
    display_order: int | None = None
