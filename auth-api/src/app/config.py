from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    auth_database_url: str = "sqlite:///./auth.db"
    cors_origins: list[str] = [
        "http://localhost:5174",
        "http://localhost:3001",
        "https://d3bwott4660u8l.cloudfront.net",
        "https://dtjlzqdyq53fa.cloudfront.net",
    ]
    jwt_secret: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    model_config = {"env_prefix": "AUTH_"}


settings = Settings()
