from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    orders_database_url: str = "sqlite:///./orders.db"
    cart_database_url: str = "sqlite:///../cart-api/cart.db"
    admin_database_url: str = "sqlite:///../admin-api/admin.db"
    cors_origins: list[str] = [
        "http://localhost:5174",
        "http://localhost:3001",
        "https://d3bwott4660u8l.cloudfront.net",
        "https://dtjlzqdyq53fa.cloudfront.net",
    ]

    model_config = {"env_prefix": "ORDERS_"}


settings = Settings()
