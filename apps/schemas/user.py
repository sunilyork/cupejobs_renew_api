from typing import Union

from beanie import Indexed
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: Union[str, None] = None
    exp: Union[int, None] = None
    iat: Union[int, None] = None
    aud: Union[str, None] = None
    iss: Union[str, None] = None


class UserCreate(BaseModel):
    """Creation user fields"""

    first_name: str
    last_name: str
    username: Indexed(str, unique=True)
    email: Indexed(str, unique=True)
    password: str
    cupe_unit: int
    cssp_eligible: bool = False
    tca_eligible: bool = False
    SISID: Union[str, None] = None
    PAYNO: Union[str, None] = None


class UserUpdate(BaseModel):
    """Updatable user fields"""

    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    username: Union[str, None] = None
    email: Union[EmailStr, None] = None
    password: Union[str, None] = None
    cupe_unit: Union[int, None] = None
    cssp_eligible: Union[str, None] = None
    tca_eligible: Union[str, None] = None
    SISID: Union[str, None] = None
    PAYNO: Union[str, None] = None
    disabled: Union[bool, None] = None

    class Config:
        schema_extra = {
            "example": {
                "first_name": "",
                "last_name": "",
                "username": "",
                "email": "",
                "password": "",
                "cupe_unit": 0,
                "cssp_eligible": False,
                "tca_eligible": False,
                "SISID": "",
                "PAYNO": "",
                "disabled": False,
            }
        }
