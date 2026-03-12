from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cart_database_url: str = "sqlite:///./cart.db"
    # shared read-only access to admin DB for product/stock data
    catalog_database_url: str = "sqlite:///../admin-api/admin.db"
    cors_origins: list[str] = [
        "http://localhost:5174",
        "http://localhost:3001",
        "https://d3bwott4660u8l.cloudfront.net",
        "https://dtjlzqdyq53fa.cloudfront.net",
    ]

    model_config = {"env_prefix": "CART_"}


settings = Settings()
