from datetime import datetime
from typing import List

import fastapi as _fastapi
from beanie import WriteRules

from apps.db.models.notification import Notification
from apps.schemas.notification import NotificationSchemaIN
from apps.db.models.user import User


async def create_user_notification(user: User, notification_in: NotificationSchemaIN):
    existing_user = await User.find_one(User.id == user.id, fetch_links=True)

    notifications = [
        notification
        for notification in existing_user.notifications
        if notification.notification_id == notification_in.notification_id.strip()
    ]

    if len(notifications) > 0:
        raise _fastapi.HTTPException(
            status_code=400, detail="Notification already exists."
        )

    notification = Notification(
        notification_id=notification_in.notification_id.strip(),
        notification_value=notification_in.notification_value.strip(),
        expire_at=notification_in.expire_at,
        read=notification_in.read,
        submission_status=notification_in.submission_status,
        description=notification_in.description,
        type=notification_in.type,
    )

    user.notifications.append(notification)
    await user.save(link_rule=WriteRules.WRITE)
    return user


async def create_user_notifications(
    user: User, notifications: List[NotificationSchemaIN]
):
    await user.fetch_all_links()
    current_notifications = user.notifications
    ids = [notification.notification_id for notification in current_notifications]
    temp_list = []
    for notification in notifications:
        if notification.notification_id not in ids:
            n = Notification(
                notification_id=notification.notification_id.strip(),
                notification_value=notification.notification_value.strip(),
                expire_at=notification.expire_at,
                read=notification.read,
                submission_status=notification.submission_status,
                description=notification.description,
                type=notification.type,
            )
            temp_list.append(n)

    user.notifications.extend(temp_list)
    await user.save(link_rule=WriteRules.WRITE)
    return user


async def get_user_notification(user: User, id: str):
    user_notification = None
    existing_user = await User.find_one(User.id == user.id, fetch_links=True)

    for notification in existing_user.notifications:
        if notification.notification_id == id.strip():
            user_notification = notification
            break

    if user_notification is None:
        raise _fastapi.HTTPException(
            status_code=400, detail="Notification does not exist."
        )

    return user_notification


async def remove_notification(user: User, id: str):
    existing_user = await User.find_one(User.id == user.id, fetch_links=True)

    notifications = [
        notification
        for notification in existing_user.notifications
        if notification.notification_id != id.strip()
    ]

    if len(existing_user.notifications) == len(notifications):
        raise _fastapi.HTTPException(
            status_code=400, detail="Notification does not exist."
        )

    for notification in existing_user.notifications:
        if notification.notification_id == id.strip():
            await notification.delete()

    existing_user.notifications = notifications
    await existing_user.save(link_rule=WriteRules.WRITE)

    return existing_user


async def remove_notifications(user: User, notification_ids: List[str]):
    ids = list(map(str.strip, notification_ids))

    existing_user = await User.find_one(User.id == user.id, fetch_links=True)

    notifications = [
        notification
        for notification in existing_user.notifications
        if notification.notification_id not in ids
    ]

    delete_notifications = [
        notification
        for notification in existing_user.notifications
        if notification.notification_id in ids
    ]

    for notification in delete_notifications:
        await notification.delete()

    existing_user.notifications = notifications
    await existing_user.save(link_rule=WriteRules.WRITE)
    return existing_user


async def update_notification(user: User, id: str, notification_data: dict):
    existing_user = await User.find_one(User.id == user.id, fetch_links=True)

    isNotificationMatch = False

    for notification_element in existing_user.notifications:
        if notification_element.notification_id == id.strip():
            isNotificationMatch = True

            if notification_data.get("read"):
                notification_element.read = notification_data["read"]
                notification_element.read_at = datetime.now()

            if notification_data.get("submission_status"):
                notification_element.submission_status = notification_data[
                    "submission_status"
                ]
                notification_element.submission_at = datetime.now()

    if isNotificationMatch:
        await existing_user.save(link_rule=WriteRules.WRITE)
        return existing_user
    else:
        raise _fastapi.HTTPException(status_code=400, detail="Document not found.")
