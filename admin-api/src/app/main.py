from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import create_tables
from app.routers import categories, images, inventory, products

app = FastAPI(title="Admin API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In local dev (no S3), serve uploaded files as static files
if not settings.s3_bucket_name:
    upload_dir = Path("uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

# Create DB tables on startup
create_tables()

# Register routers
PREFIX = "/admin"
app.include_router(categories.router, prefix=PREFIX)
app.include_router(products.router, prefix=PREFIX)
app.include_router(images.router, prefix=PREFIX)
app.include_router(inventory.router, prefix=PREFIX)


@app.get("/health")
def health():
    return {"status": "ok"}
