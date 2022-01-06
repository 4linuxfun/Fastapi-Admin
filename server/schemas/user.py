from typing import List
from ..sql.models import User
from pydantic import BaseModel


class UserInfo(BaseModel):
    user: User
    roles: List[str]


class UserLogin(BaseModel):
    username: str
    password: str
