from pydantic import BaseModel
from typing import List, Optional, Any


class Common(BaseModel):
    code: int
    message: str
    data: Any


class UserName(BaseModel):
    username: str
    disabled: bool


class UserRoles(UserName):
    roles: List[str]


class UserInfo(UserRoles):
    email: Optional[str]
    avater: Optional[str]
