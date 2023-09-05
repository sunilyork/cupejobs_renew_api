import calendar
from datetime import datetime, timedelta
from typing import Union

from cryptography.hazmat.primitives import serialization
from jose import jwt

from apps.config import get_settings

settings = get_settings()


def create_access_token(
    data: dict,
    expires_delta: Union[timedelta, None] = None,
):
    expire = 0
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": f"users/api/user/me",
        }
    )

    with open(settings.JWT_ACCESS_TOKEN_SECRET_KEY_PRIVATE_KEY, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=bytes(settings.JWT_SECRET_KEY_ID_RSA_PASSWORD, "utf-8"),
        )

    key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    encoded_jwt = jwt.encode(to_encode, key, algorithm="RS256")

    access_token_expire = calendar.timegm(expire.timetuple())

    return {
        "access_token": encoded_jwt,
        "access_token_expire": access_token_expire,
        "token_type": "bearer",
    }


def create_refresh_token(
    data: dict,
    expires_delta: Union[timedelta, None] = None,
):
    expire = 0
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": f"users/api/user/me",
        }
    )

    with open(settings.JWT_REFRESH_TOKEN_SECRET_KEY_PRIVATE_KEY, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=bytes(settings.JWT_SECRET_KEY_ID_RSA_PASSWORD, "utf-8"),
        )

    key = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )

    encoded_jwt = jwt.encode(to_encode, key, algorithm="RS256")

    return {"refresh_token": encoded_jwt, "token_type": "bearer"}
