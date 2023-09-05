import logging

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from apps.config import get_settings
from apps.db.models import all_models

settings = get_settings()
logger = logging.getLogger(__name__)


async def init_database_connection():
    mongodb_client = AsyncIOMotorClient(settings.DB_URL)
    await init_beanie(
        database=mongodb_client[settings.DB_NAME], document_models=all_models
    )
    logger.info(f"Connected to {settings.DB_URL} and DB_NAME:{settings.DB_NAME}")
    return mongodb_client
