import datetime as _dt
from typing import List, Optional

from beanie import Document, Link
from bson import ObjectId
from passlib import hash as _hash
from pydantic import Field

from apps.db.models.notification import Notification
from apps.lib.helper import PyObjectId
from apps.schemas.user import UserCreate


class User(Document, UserCreate):
    """Users DB representation"""

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    notifications: Optional[List[Link[Notification]]] = []
    disabled: Optional[bool] = Field(default=False)
    created_at: _dt.datetime = Field(default_factory=_dt.datetime.now)
    last_login: _dt.datetime = Field(default_factory=_dt.datetime.now)

    def __repr__(self) -> str:
        return f"<User {self.email}>"

    def __str__(self) -> str:
        return self.email

    def __hash__(self) -> int:
        return hash(self.email)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, User):
            return self.email == other.email
        return False

    @property
    def created(self) -> _dt.datetime:
        """Datetime user was created from ID"""
        return self.id.generation_time

    @classmethod
    async def by_email(cls, email: str) -> "User":
        """Get a user by email"""
        return await cls.find_one(cls.email == email)

    @classmethod
    async def by_username(cls, username: str) -> "User":
        """Get a user by username"""
        return await cls.find_one(cls.username == username)

    @classmethod
    async def by_userid(cls, userid: str) -> "User":
        """Get a user by userid"""
        return await cls.find_one(cls.id == userid)

    def verify_password(self, password: str):
        return _hash.bcrypt.verify(password, self.password)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  # required for the _id
        json_encoders = {ObjectId: str}

    class Settings:
        name = "users"
