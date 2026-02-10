from functools import lru_cache
from typing import List

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    mongo_uri: AnyUrl = Field(alias="MONGO_URI")
    db_name: str = Field(default="swifteats", alias="DB_NAME")

    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=1440, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    cors_origins: List[str] = Field(default_factory=lambda: ["*"], alias="CORS_ORIGINS")

    delivery_fee: float = Field(default=5.0, alias="DELIVERY_FEE")
    free_delivery_threshold: float = Field(default=25.0, alias="FREE_DELIVERY_THRESHOLD")
    tracking_eta_seconds: int = Field(default=60, alias="TRACKING_ETA_SECONDS")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]


settings = get_settings()



