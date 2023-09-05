import email_validator as _email_check
import fastapi as _fastapi
import requests
from cryptography.hazmat.primitives import serialization
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from apps.config import get_settings, pwd_context
from apps.core import constants
from apps.core.constants import CupeUnit
from apps.db.models.user import User
from apps.lib import helper
from apps.schemas.user import TokenPayload

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/api/token")


async def create_user(user_create: User):
    try:
        valid = _email_check.validate_email(email=user_create.email)

        email = valid.email
    except _email_check.EmailNotValidError:
        raise _fastapi.HTTPException(status_code=404, detail="Invalid email entered.")

    if not helper.is_valid_password(user_create.password):
        raise HTTPException(status_code=400, detail="Invalid password.")

    hash_password = pwd_context.hash(user_create.password)

    encrpty_SISID = ""
    if user_create.SISID:
        encrpty_SISID = helper.encrypt_message(user_create.SISID)

    encrpty_PAYNO = ""
    if user_create.PAYNO:
        encrpty_PAYNO = helper.encrypt_message(user_create.PAYNO)

    cssp = False
    tca = False
    if user_create.PAYNO and user_create.cupe_unit == int(CupeUnit.CUPE_2):
        headers = {"payno": user_create.PAYNO}
        resp = requests.get(constants.CSSP_ELIGIBILITY_URL, headers=headers)
        cssp = resp.json()

        resp = requests.get(constants.TCA_ELIGIBILITY_URL, headers=headers)
        tca = resp.json()

    user_obj = User(
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        username=user_create.username,
        email=email,
        password=hash_password,
        cupe_unit=user_create.cupe_unit,
        cssp_eligible=cssp,
        tca_eligible=tca,
        SISID=encrpty_SISID,
        PAYNO=encrpty_PAYNO,
    )
    await user_obj.create()
    return user_obj


async def authenticate_user(username: str, password: str):
    user = await User.find_one(User.username == username)
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user


async def refresh_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        with open(settings.JWT_REFRESH_TOKEN_SECRET_KEY_PUBLIC_KEY, "rb") as key_file:
            public_key = serialization.load_pem_public_key(key_file.read())

        header_data = jwt.get_unverified_header(token)

        payload = jwt.decode(
            token=token,
            key=public_key,
            algorithms=[
                header_data["alg"],
            ],
        )

        userid: str = payload.get("sub")

        if userid is None:
            raise credentials_exception

        token_data = TokenPayload(**payload)
    except JWTError:
        print("service.py -> refresh_token -> JWTError!")
        raise credentials_exception
    user = await User.by_userid(helper.PyObjectId(token_data.sub))
    if user is None:
        print("service.py -> refresh_token -> user none!")
        raise credentials_exception
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        with open(settings.JWT_ACCESS_TOKEN_SECRET_KEY_PUBLIC_KEY, "rb") as key_file:
            public_key = serialization.load_pem_public_key(key_file.read())

        header_data = jwt.get_unverified_header(token)

        payload = jwt.decode(
            token=token,
            key=public_key,
            algorithms=[
                header_data["alg"],
            ],
        )

        userid: str = payload.get("sub")

        if userid is None:
            raise credentials_exception

        token_data = TokenPayload(**payload)
    except JWTError:
        raise credentials_exception
    user = await User.by_userid(helper.PyObjectId(token_data.sub))
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user.")
    return current_user
