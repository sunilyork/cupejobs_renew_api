import asyncio
import datetime as _dt
import os

import pytest
import pytest_asyncio
from beanie import WriteRules, init_beanie
from bson import ObjectId
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from apps.config import get_settings
from apps.core.constants import NotificationType
from apps.db.models import all_models
from apps.db.models.notification import Notification
from apps.db.models.user import User
from main import app

settings = get_settings()


@pytest_asyncio.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


def pytest_sessionfinish(session, exitstatus):
    asyncio.get_event_loop().close()


@pytest_asyncio.fixture(scope="session")
async def async_app_client():
    async with AsyncClient(app=app, base_url="http://localhost:8001") as client:
        if os.getenv("ENVIRONMENT").lower() != "test":
            pytest.exit("PyTest --- Set ENVIRONMENT=test in pytest.ini file")
        if settings.DB_NAME != "testdb":
            pytest.exit("PyTest --- Set DB_NAME=testdb in .env.test file")
        else:
            client.app = app
            await setup()
            yield client
            await teardown()


async def setup():
    app.mongodb_client = AsyncIOMotorClient(settings.DB_URL)
    app.mongodb = app.mongodb_client[settings.DB_NAME]
    await init_beanie(database=app.mongodb, document_models=all_models)
    await init_data()


async def teardown():
    await clear_data()
    app.mongodb_client.close()


async def clear_data():
    await User.find_all().delete()
    await Notification.find_all().delete()


async def init_data():
    notification1 = Notification(
        id=ObjectId("625ea3875b0cdf6389fc64aa"),
        notification_id="test1",
        notification_value="existing_notification",
        created_at=_dt.datetime(2015, 4, 30, 3, 20, 6),
        expire_at=_dt.datetime(2016, 4, 30, 3, 20, 6),
        read=False,
        submission_status=False,
        description="description 1",
        read_at=None,
        submission_at=None,
        type=NotificationType.BLANKET,
    )
    notification2 = Notification(
        id=ObjectId("625ea3875b0cdf6389fc64ab"),
        notification_id="test2",
        notification_value="test_notification_update",
        created_at=_dt.datetime(2015, 4, 30, 3, 20, 6),
        expire_at=_dt.datetime(2016, 4, 30, 3, 20, 6),
        read=False,
        submission_status=False,
        description="description 2",
        read_at=None,
        submission_at=None,
        type=NotificationType.BLANKET,
    )
    notification3 = Notification(
        id=ObjectId("625ea3875b0cdf6389fc64ac"),
        notification_id="test3",
        notification_value="test_notification_update",
        created_at=_dt.datetime(2015, 4, 30, 3, 20, 6),
        expire_at=_dt.datetime(2016, 4, 30, 3, 20, 6),
        read=False,
        submission_status=False,
        description="description 3",
        read_at=None,
        submission_at=None,
        type=NotificationType.POSTING,
    )

    user1 = User(
        id=ObjectId("625ea3875b0cdf6389fc64ba"),
        first_name="tom",
        last_name="wright",
        username="tomwright",
        email="tom@gmail.com",
        password="$2b$12$FnHp4XQJNT04Vjsp1c1VlOCE33uymeySngxfKGava2CNSooZxttrG",
        cupe_unit=1,
        SISID="string",
        PAYNO="payno",
    )
    user1.notifications = [notification1]

    user2 = User(
        id=ObjectId("625ea3875b0cdf6389fc64bb"),
        first_name="john",
        last_name="wright",
        username="johnwright",
        email="duplicate_email@gmail.com",
        password="Password123#",
        cupe_unit=1,
        SISID="string",
        PAYNO="payno",
    )

    user3 = User(
        id=ObjectId("625ea3875b0cdf6389fc64bc"),
        first_name="string",
        last_name="string",
        username="string",
        email="currentuser1@gmail.com",
        password="String123$",
        cupe_unit=1,
        SISID="string",
        PAYNO="string",
        notifications=[notification2, notification3],
    )

    user1.notifications.append(notification1)
    await user1.save(link_rule=WriteRules.WRITE)

    await user2.save(link_rule=WriteRules.WRITE)

    user3.notifications.append(notification2)
    user3.notifications.append(notification3)
    await user3.save(link_rule=WriteRules.WRITE)
