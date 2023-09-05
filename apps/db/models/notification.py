import datetime as _dt
from typing import Optional

from beanie import Document
from bson import ObjectId
from pydantic import Field

from apps.lib.helper import PyObjectId
from apps.schemas.notification import NotificationSchemaIN


class Notification(Document, NotificationSchemaIN):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: _dt.datetime = Field(default_factory=_dt.datetime.now)
    read_at: Optional[_dt.datetime] = Field(
        None, example=_dt.datetime(1, 1, 1, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
    )
    submission_at: Optional[_dt.datetime] = Field(
        None, example=_dt.datetime(1, 1, 1, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
    )

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}

    class Settings:
        name = "notifications"
