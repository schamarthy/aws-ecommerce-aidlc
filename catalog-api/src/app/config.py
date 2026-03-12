from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Points at the admin-api database (shared read-only access)
    database_url: str = "sqlite:///../admin-api/admin.db"
    cors_origins: list[str] = [
        "http://localhost:5174",
        "http://localhost:3001",
        "https://d3bwott4660u8l.cloudfront.net",
        "https://dtjlzqdyq53fa.cloudfront.net",
    ]
    default_page_size: int = 20

    model_config = {"env_prefix": "CATALOG_"}


settings = Settings()
