import datetime as _dt
from typing import Union

from pydantic import BaseModel


class NotificationSchemaIN(BaseModel):
    notification_id: str
    notification_value: str
    expire_at: _dt.datetime
    read: bool = False
    submission_status: bool = False
    description: str
    type: str


class UpdateNotification(BaseModel):
    read: Union[bool, None] = None
    submission_status: Union[bool, None] = None

    class Config:
        schema_extra = {
            "example": {
                "read": False,
                "submission_status": False,
            }
        }
