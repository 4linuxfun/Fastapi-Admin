from typing import Optional, List, Literal, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from .relationships import UserRole
from .role import Role

if TYPE_CHECKING:
    from .role import Role


class UserWithOutPasswd(SQLModel):
    name: str = Field(..., min_length=5, max_length=50)
    enable: int
    avatar: Optional[str]
    email: Optional[str]


class UserBase(UserWithOutPasswd):
    password: Optional[str]
    # age: Optional[int] = Field(..., title='年龄', lt=120)


class UserRead(UserBase):
    # get请求时返回的数据模型，response_model使用模型
    id: int


class UserReadWithRoles(UserRead):
    # 包含relationship的数据模型
    roles: List['Role'] = []


class UserRoles(SQLModel):
    roles: List['Role'] = []
    enable: List[str] = []


class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    roles: List['Role'] = Relationship(back_populates="users", link_model=UserRole)


class UserCreateWithRoles(SQLModel):
    # POST请求时，传递过来的模型
    user: UserBase
    roles: List[int]

    class Config:
        title = '新建用户'


class UserUpdatePassword(SQLModel):
    id: int
    password: str


class UserUpdateWithRoles(SQLModel):
    # PUT请求时，传递过来的数据模型
    user: UserWithOutPasswd
    roles: List[int]


class UserLogin(SQLModel):
    username: str
    password: str


class LoginResponse(SQLModel):
    uid: int
    token: str
