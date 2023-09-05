import datetime as _dt

import pytest
from bson import ObjectId
from starlette.testclient import TestClient

import apps.lib.services as _services
from apps.core.constants import NotificationType
from apps.db.models.notification import Notification
from apps.db.models.user import User
from main import app

client = TestClient(app)


def get_current_user():
    notification2 = Notification(
        id=ObjectId("625ea3875b0cdf6389fc64ab"),
        notification_id="test1",
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
        notification_id="test2",
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

    user = User(
        _id=ObjectId("625ea3875b0cdf6389fc64bc"),
        first_name="string",
        last_name="string",
        username="username5",
        email="username5@gmail.com",
        password="string",
        cupe_unit=0,
        SISID="string",
        PAYNO="string",
        notifications=[notification2, notification3],
    )
    return user


app.dependency_overrides[_services.get_current_user] = get_current_user


@pytest.mark.asyncio
async def test_create_user_invalid_email_throws_error(async_app_client):
    user_json = {
        "first_name": "string",
        "last_name": "string",
        "username": "non-existent username",
        "email": "invalid email",
        "password": "string",
        "cupe_unit": 0,
        "SISID": "string",
        "PAYNO": "string",
    }
    response = await async_app_client.post("/users/api/user", json=user_json)
    assert response.status_code == 404
    assert response.json() == {"detail": "Invalid email entered."}


@pytest.mark.asyncio
async def test_create_user_duplicate_email_throws_error(async_app_client, mocker):
    user_json = {
        "first_name": "string",
        "last_name": "string",
        "username": "username2",
        "email": "duplicate_email@gmail.com",
        "password": "string",
        "cupe_unit": 0,
        "SISID": "string",
        "PAYNO": "string",
    }

    mocker.patch("apps.lib.services.helper.encrypt_message", return_value="encrypted_")
    response = await async_app_client.post("/users/api/user", json=user_json)
    assert response.status_code == 400
    assert response.json() == {"detail": "Please use different email or username."}


@pytest.mark.asyncio
async def test_create_user_valid_unique_email_creates_user(async_app_client, mocker):
    user_json = {
        "first_name": "string",
        "last_name": "string",
        "username": "username3",
        "email": "testuser1@gmail.com",
        "password": "String123^",
        "cupe_unit": 1,
        "SISID": "string",
        "PAYNO": "string",
    }

    mocker.patch(
        "apps.lib.services.helper.encrypt_message",
        return_value="encrypted_str",
    )

    response = await async_app_client.post("/users/api/user", json=user_json)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_generate_token_should_return_token_for_authorized_user(
    async_app_client, mocker
):
    user_json = {
        "first_name": "testuser1",
        "last_name": "testuser1",
        "username": "username4",
        "email": "testuser1@yorku.ca",
        "password": "Password123^",
        "cupe_unit": 1,
        "SISID": "string",
        "PAYNO": "string",
    }

    mocker.patch(
        "apps.lib.services.helper.encrypt_message",
        return_value="encrypted_str",
    )

    response = await async_app_client.post("/users/api/user", json=user_json)

    user = await User.find_one(User.email == "testuser1@yorku.ca")
    form_data = {
        "grant_type": "password",
        "username": user.username,
        "password": "Password123^",
        "scopes": [],
        "client_id": None,
        "client_secret": None,
    }
    response = await async_app_client.post(
        "/users/api/token",
        data=form_data,
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    response = await async_app_client.get("/users/api/logout")


@pytest.mark.asyncio
async def test_generate_token_should_fail_for_unauthorized_user(
    async_app_client, mocker
):
    form_data = {
        "grant_type": "password",
        "username": "tom@gmail.com",
        "password": "wrong_password",
        "scopes": [],
        "client_id": None,
        "client_secret": None,
    }
    mocker.patch("fastapi.Request.cookies", {"refresh_token": "1234"})
    response = await async_app_client.post(
        "/users/api/token",
        data=form_data,
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_user_throws_error_when_not_authenticated(async_app_client, mocker):
    mocker.patch(
        "apps.lib.services.helper.decrypt_message",
        return_value="decrypted_str",
    )

    # Logout user if already logged in from a previous unit test
    response = await async_app_client.get("/users/api/logout")
    assert response.status_code == 200

    response = await async_app_client.get("/users/api/user/me")
    assert response.status_code == 400
