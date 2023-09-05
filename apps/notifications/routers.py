from typing import List

import fastapi as _fastapi
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.params import Body
from fastapi.responses import JSONResponse

import apps.lib.services as _services
from apps.schemas.notification import NotificationSchemaIN, UpdateNotification
from apps.db.models.user import User
from apps.lib.user_notification import (
    create_user_notification,
    create_user_notifications,
    get_user_notification,
    remove_notification,
    remove_notifications,
)

router = APIRouter()


@router.post("/", response_description="Add user notification")
async def create_notification(
    request: Request,
    notification_in: NotificationSchemaIN,
    user: User = _fastapi.Depends(_services.get_current_user),
):
    if request.cookies.get("refresh_token"):
        existing_user = await create_user_notification(
            user=user, notification_in=notification_in
        )

        if existing_user:
            result = jsonable_encoder(existing_user.notifications.pop())
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"notification": result},
            )
    else:
        raise HTTPException(status_code=400, detail="Could not validate credentials.")


@router.post("/addbatch", response_description="Add user notifications")
async def create_notifications(
    request: Request,
    notifications: List[NotificationSchemaIN] = Body(
        default=None, description="List of notifications"
    ),
    user: User = _fastapi.Depends(_services.get_current_user),
):
    if request.cookies.get("refresh_token"):
        existing_user = await create_user_notifications(
            user=user, notifications=notifications
        )
        return existing_user.notifications
    else:
        raise HTTPException(status_code=400, detail="Could not validate credentials.")


@router.get("/", response_description="Get user notifications")
async def get_notifications(
    request: Request,
    user: User = _fastapi.Depends(_services.get_current_user),
):
    if request.cookies.get("refresh_token"):
        existing_user = await User.find_one(User.id == user.id, fetch_links=True)
        return existing_user.notifications
    else:
        raise HTTPException(status_code=400, detail="Could not validate credentials.")


@router.get("/{id}", response_description="Get user notification")
async def get_notification(
    request: Request,
    id: str,
    user: User = _fastapi.Depends(_services.get_current_user),
):
    if request.cookies.get("refresh_token"):
        user_notification = await get_user_notification(user=user, id=id)
        return user_notification
    else:
        raise HTTPException(status_code=400, detail="Could not validate credentials.")


@router.patch("{id}", response_description="Update user notification")
async def update_notification(
    *,
    request: Request,
    id: str,
    user: User = _fastapi.Depends(_services.get_current_user),
    notification_data: UpdateNotification,
):
    if request.cookies.get("refresh_token"):
        current_user = await update_notification(
            user=user,
            id=id,
            notification_data=notification_data.dict(exclude_unset=True),
        )
        if current_user:
            return JSONResponse(
                content={"detail": "Successfully update."}, status_code=200
            )
    else:
        raise HTTPException(status_code=400, detail="Could not validate credentials.")


@router.delete("/{id}", response_description="Delete user notification")
async def delete_notification(
    request: Request,
    id: str,
    user: User = _fastapi.Depends(_services.get_current_user),
):
    if request.cookies.get("refresh_token"):
        user = await remove_notification(user=user, id=id)

        if user:
            return JSONResponse(
                content={"detail": "Successfully deleted."},
                status_code=status.HTTP_200_OK,
            )
    else:
        raise HTTPException(status_code=400, detail="Could not validate credentials.")


@router.post("/deletebatch", response_description="Delete user notifications")
async def delete_notifications(
    request: Request,
    notification_ids: List[str] = Body(
        default=None, description="List of notification id's"
    ),
    user: User = _fastapi.Depends(_services.get_current_user),
):
    if request.cookies.get("refresh_token"):
        await remove_notifications(user, notification_ids)
        existing_user = await User.find_one(User.id == user.id, fetch_links=True)
        return existing_user.notifications
    else:
        raise HTTPException(status_code=400, detail="Could not validate credentials.")
