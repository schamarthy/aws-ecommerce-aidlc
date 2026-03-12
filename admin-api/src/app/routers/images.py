from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.product_image import ProductImage
from app.schemas.image import ImageOut, ImageUpdate
from app.services.image_service import delete_file, save_upload

router = APIRouter(tags=["images"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


@router.post("/products/{product_id}/images", response_model=ImageOut, status_code=201)
async def upload_image(
    product_id: int,
    file: UploadFile,
    is_primary: bool = False,
    display_order: int = 0,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    url = await save_upload(file, product_id)

    if is_primary:
        db.query(ProductImage).filter(ProductImage.product_id == product_id).update(
            {"is_primary": False}
        )

    img = ProductImage(
        product_id=product_id,
        storage_url=url,
        is_primary=is_primary,
        display_order=display_order,
    )
    db.add(img)
    db.commit()
    db.refresh(img)
    return img


@router.put("/products/{product_id}/images/{image_id}", response_model=ImageOut)
def update_image(
    product_id: int,
    image_id: int,
    data: ImageUpdate,
    db: Session = Depends(get_db),
):
    img = (
        db.query(ProductImage)
        .filter(ProductImage.id == image_id, ProductImage.product_id == product_id)
        .first()
    )
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")

    updates = data.model_dump(exclude_unset=True)
    if updates.get("is_primary"):
        db.query(ProductImage).filter(ProductImage.product_id == product_id).update(
            {"is_primary": False}
        )
    for field, val in updates.items():
        setattr(img, field, val)
    db.commit()
    db.refresh(img)
    return img


@router.delete("/products/{product_id}/images/{image_id}", status_code=204)
def delete_image(product_id: int, image_id: int, db: Session = Depends(get_db)):
    img = (
        db.query(ProductImage)
        .filter(ProductImage.id == image_id, ProductImage.product_id == product_id)
        .first()
    )
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    delete_file(img.storage_url)
    db.delete(img)
    db.commit()
