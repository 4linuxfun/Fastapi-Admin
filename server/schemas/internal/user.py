from typing import List
from pydantic import BaseModel
from ...models.internal import User


class UserInfo(BaseModel):
    user: User
    roles: List[str]


class UserLogin(BaseModel):
    username: str
    password: str
