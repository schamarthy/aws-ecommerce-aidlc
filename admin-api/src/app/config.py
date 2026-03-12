from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./admin.db"
    s3_bucket_name: str = ""
    s3_images_cloudfront_url: str = ""
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "https://d3bwott4660u8l.cloudfront.net",
        "https://dtjlzqdyq53fa.cloudfront.net",
    ]

    model_config = {"env_prefix": "ADMIN_"}


settings = Settings()
