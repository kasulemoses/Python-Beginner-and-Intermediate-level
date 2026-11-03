from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    mongodb_uri: str | None = None
    mongodb_database: str = Field(default="python_learning", pattern=r"^[A-Za-z0-9_-]+$")
    cors_origins: list[str] = ["http://localhost:3000"]
