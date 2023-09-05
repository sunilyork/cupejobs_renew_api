from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

import apps.lib.services as _services
import apps.lib.user
import apps.lib.user_notification
from apps.config import get_settings
from apps.core.security import create_access_token, create_refresh_token
from apps.db.models.user import User
from apps.lib import helper as _helper
from apps.schemas.user import UserCreate, UserUpdate

settings = get_settings()

router = APIRouter()


@router.post("/api/user", response_description="Add user")
async def create_user(response: Response, user_create: UserCreate):
    user = await User.by_email(user_create.email)

    if user:
        raise HTTPException(
            status_code=400,
            detail="Please use different email or username.",
        )

    user = await User.by_username(user_create.username)

    if user:
        raise HTTPException(
            status_code=400,
            detail="Please use different email or username.",
        )

    user_obj = await _services.create_user(user_create=user_create)
    if user_obj:
        new_user = await User.by_email(user_obj.email)
        access_token = await generate_tokens(response, new_user)
        return access_token


@router.post("/api/token", response_description="Create access and refresh tokens")
async def generate_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await _services.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = await generate_tokens(response, user)

    return access_token


async def generate_tokens(response, user):
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token.get("token_type")
        + " "
        + refresh_token.get("refresh_token"),
        httponly=True,
        samesite="lax",
        # secure=True,  # In production check uncomment to secure=true
    )
    return access_token


@router.post("/api/refresh", response_description="Re-create access token")
async def refresh(request: Request):
    print(
        f"refresh endpoint - > refresh_token: {request.cookies.get('refresh_token')}\n"
    )
    if request.cookies.get("refresh_token"):
        user = await _services.refresh_token(
            request.cookies.get("refresh_token").split(" ")[1]
        )

        if user:
            access_token = create_access_token(
                data={"sub": str(user.id)},
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            )

            print(f"refresh endpoint -> access_token: {access_token}\n")

            return access_token
    else:
        print("router.py -> refresh -> Session expired!")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Session expired"
        )


@router.get("/api/logout", response_description="Logout user")
async def logout(response: Response, request: Request):
    print(
        f"logout endpoint --> refresh_token: {request.cookies.get('refresh_token')}\n"
    )
    response.delete_cookie(key="refresh_token")
    if request.cookies.get("refresh_token"):
        expires = datetime.utcnow() + timedelta(seconds=1)
        response.set_cookie(
            key="refresh_token",
            value="",
            # secure=True,  # In production check uncomment to secure=true
            httponly=True,
            samesite="lax",
            expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        )
        print(
            f"logout if exist refresh_token: {request.cookies.get('refresh_token')}\n"
        )
        return {"detail": "Successfully logout."}
    else:
        print(
            f"logout if not exist or expire refresh_token: {request.cookies.get('refresh_token')}\n"
        )
        expires = datetime.utcnow() + timedelta(seconds=1)
        response.set_cookie(
            key="refresh_token",
            value="",
            # secure=True,  # In production check uncomment to secure=true
            httponly=True,
            samesite="lax",
            expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        )
        return {"detail": "Session expired."}


@router.get("/api/user/me", response_description="Get user information")
async def read_users_me(
    request: Request,
    current_user: User = Depends(_services.get_current_active_user),
):
    if request.cookies.get("refresh_token"):
        return _helper.user_dict(current_user)
    else:
        raise HTTPException(status_code=400, detail="Could not validate credentials.")


@router.patch("/api/user/me", response_description="Update user")
async def current_user_data_update(
    *,
    request: Request,
    current_uer_update_data: UserUpdate,
    current_user: User = Depends(_services.get_current_active_user),
):
    if request.cookies.get("refresh_token"):
        updated_user = await apps.lib.user.update_user(
            user_id=current_user.id,
            user_data=current_uer_update_data.dict(exclude_unset=True),
        )
        if updated_user:
            return "Successfully updates."
        raise HTTPException(status_code=400, detail="No update applies.")
    else:
        raise HTTPException(status_code=400, detail="Could not validate credentials.")
