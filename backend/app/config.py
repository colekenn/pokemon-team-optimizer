from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://pokemon:pokemon@localhost:5433/pokemon"
    redis_url: str = "redis://localhost:6380/0"
    cache_ttl_seconds: int = 86400
    cors_origins: str = "http://localhost:5173"


settings = Settings()
