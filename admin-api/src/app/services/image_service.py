import uuid
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from app.config import settings


def _use_s3() -> bool:
    return bool(settings.s3_bucket_name)


async def save_upload(file: UploadFile, product_id: int) -> str:
    """Upload file to S3 (production) or local disk (dev) and return the URL."""
    ext = Path(file.filename or "image.bin").suffix
    filename = f"{uuid.uuid4().hex}{ext}"
    content = await file.read()

    if _use_s3():
        key = f"uploads/{product_id}/{filename}"
        s3 = boto3.client("s3")
        s3.put_object(
            Bucket=settings.s3_bucket_name,
            Key=key,
            Body=content,
            ContentType=file.content_type or "application/octet-stream",
        )
        base = settings.s3_images_cloudfront_url.rstrip("/")
        return f"{base}/{key}"
    else:
        # Local dev fallback
        import aiofiles
        upload_dir = Path("uploads") / str(product_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        dest = upload_dir / filename
        async with aiofiles.open(dest, "wb") as out:
            await out.write(content)
        return f"/uploads/{product_id}/{filename}"


def delete_file(storage_url: str) -> None:
    """Delete file from S3 (production) or local disk (dev)."""
    if _use_s3() and storage_url.startswith("http"):
        # Extract S3 key from CloudFront URL
        base = settings.s3_images_cloudfront_url.rstrip("/")
        key = storage_url.replace(base + "/", "")
        try:
            s3 = boto3.client("s3")
            s3.delete_object(Bucket=settings.s3_bucket_name, Key=key)
        except ClientError:
            pass
    else:
        import os
        relative = storage_url.lstrip("/")
        path = Path(relative)
        if path.exists():
            os.remove(path)
