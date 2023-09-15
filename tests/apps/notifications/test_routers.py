import json

import pytest
from fastapi.encoders import jsonable_encoder
from starlette.testclient import TestClient

import apps.lib.services as _services
from apps.core.constants import NotificationType
from apps.db.models.user import User
from main import app

client = TestClient(app)


async def get_user_with_zero_notifications():
    user = await User.find_one(User.email == "duplicate_email@gmail.com")
    return user


async def get_current_user():
    user = await User.find_one(User.email == "tom@gmail.com")
    return user


async def get_user_with_two_notifications():
    user = await User.find_one(User.email == "currentuser1@gmail.com")
    return user


@pytest.mark.asyncio
async def test_get_notifications_fails_credential_validation_for_missing_refresh_token(
    async_app_client, mocker
):
    app.dependency_overrides[
        _services.get_current_user
    ] = get_user_with_zero_notifications
    mocker.patch("fastapi.Request.cookies", {"random_attr": "1234"})

    response = await async_app_client.get("/notifications/")
    assert response.status_code == 400
    response.json() == {"detail": "Could not validate credentials."}


@pytest.mark.asyncio
async def test_get_notifications_returns_empty_list_for_user_without_notifications(
    async_app_client, mocker
):
    app.dependency_overrides[
        _services.get_current_user
    ] = get_user_with_zero_notifications
    mocker.patch("fastapi.Request.cookies", {"refresh_token": "1234"})

    response = await async_app_client.get("/notifications/")
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_get_notifications_returns_non_empty_list_for_user_with_notifications(
    async_app_client, mocker
):
    app.dependency_overrides[
        _services.get_current_user
    ] = get_user_with_two_notifications
    mocker.patch("fastapi.Request.cookies", {"refresh_token": "1234"})

    response = await async_app_client.get("/notifications/")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_create_user_notification_should_update_with_new_notification(
    async_app_client, mocker
):
    app.dependency_overrides[_services.get_current_user] = get_current_user
    mocker.patch("fastapi.Request.cookies", {"refresh_token": "1234"})
    notification = {
        "notification_id": "test3",
        "notification_value": "new_notification",
        "expire_at": "2022-05-24T21:17:33.371Z",
        "read": False,
        "submission_status": False,
        "description": "string",
        "type": NotificationType.BLANKET.value,
    }

    response = await async_app_client.post(
        "/notifications/", json=jsonable_encoder(notification)
    )

    result = json.loads(response.__dict__["_content"].decode("utf-8"))
    assert result["notification"]["notification_id"] == "test3"
    assert result["notification"]["notification_value"] == "new_notification"
    assert result["notification"]["read"] is False
    assert result["notification"]["submission_status"] is False


@pytest.mark.asyncio
async def test_delete_notification_should_throw_error_when_notification_does_not_exist(
    async_app_client, mocker
):
    app.dependency_overrides[_services.get_current_user] = get_current_user
    mocker.patch("fastapi.Request.cookies", {"refresh_token": "1234"})

    response = await async_app_client.delete("/notifications/non-existing_notification")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_notification_should_remove_user_notification(
    async_app_client, mocker
):
    app.dependency_overrides[_services.get_current_user] = get_current_user
    mocker.patch("fastapi.Request.cookies", {"refresh_token": "1234"})

    response = await async_app_client.delete("/notifications/test1")
    print(f"Response: {response.__dict__}")
    assert response.status_code == 200
