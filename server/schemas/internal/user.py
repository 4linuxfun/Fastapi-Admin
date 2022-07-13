from typing import List, Dict
from pydantic import BaseModel
from ...models.internal.user import UserWithOutPasswd, User


class UserInfo(BaseModel):
    user: User
    roles: List[str]


class UserLogin(BaseModel):
    username: str
    password: str


class UserSearch(UserWithOutPasswd):
    type: Dict[str, str]
