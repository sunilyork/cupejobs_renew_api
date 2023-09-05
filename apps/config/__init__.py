import os
import sys
from functools import lru_cache

from passlib.context import CryptContext
from pydantic import BaseSettings

USE_CACHED_SETTINGS = os.getenv("USE_CACHED_SETTINGS", "TRUE").lower == "true"
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CommonSettings(BaseSettings):
    APP_NAME: str = "CUPE Jobs"
    DEBUG_MODE: bool = False


class ServerSettings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8001


class DatabaseSettings(BaseSettings):
    DB_URL: str
    DB_NAME: str


class ArmsSettings(BaseSettings):
    ARMS_API_URL: str
    CUPEJOBS_UI_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days


class SSHSettings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_SECRET_KEY_ID_RSA_PASSWORD: str
    JWT_ACCESS_TOKEN_SECRET_KEY_PRIVATE_KEY: str
    JWT_ACCESS_TOKEN_SECRET_KEY_PUBLIC_KEY: str
    JWT_REFRESH_TOKEN_SECRET_KEY_PRIVATE_KEY: str
    JWT_REFRESH_TOKEN_SECRET_KEY_PUBLIC_KEY: str


class Settings(
    ArmsSettings, CommonSettings, ServerSettings, DatabaseSettings, SSHSettings
):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


pwd_context = CryptContext(
    schemes=["bcrypt"], default="bcrypt", bcrypt__rounds=14, deprecated="auto"
)


@lru_cache()
def get_cached_settings():
    """
    https://hindenes.com/testing-fastapi-basesettings
    Bypass pydantic's class instantiation by caching the method
    """
    return Settings()


def get_settings() -> Settings:
    if (
        os.getenv("ENVIRONMENT") is not None
        and os.getenv("ENVIRONMENT").lower() == "test"
    ):
        if not os.path.isfile(os.path.join(ROOT_DIR, ".env.test")):
            print("Running pytest: .env.test file not found in project root directory.")
            sys.exit()
        else:
            return Settings(_env_file=os.path.join(ROOT_DIR, ".env.test"))
    else:
        if USE_CACHED_SETTINGS:
            return get_cached_settings()
        else:
            return Settings()
