from typing import Optional, List, Literal, TYPE_CHECKING
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship, Column, Integer, Boolean
from .relationships import UserRole, UserJob
from .role import Role

if TYPE_CHECKING:
    from .role import Role
    from .job import Job


class UserWithOutPasswd(SQLModel):
    name: str = Field(max_length=20, sa_column_kwargs={'unique': True, 'comment': '用户名'})
    enable: bool = Field(default=True, sa_column=Column(Boolean, comment='可用'))
    avatar: Optional[str] = Field(max_length=100, sa_column_kwargs={'comment': '头像'})
    email: Optional[str] = Field(max_length=20, sa_column_kwargs={'comment': '邮箱'})


class UserBase(UserWithOutPasswd):
    password: Optional[str] = Field(max_length=50, sa_column_kwargs={'comment': '密码'})
    # age: Optional[int] = Field(..., title='年龄', lt=120)


class UserRead(UserWithOutPasswd):
    # get请求时返回的数据模型，response_model使用模型
    id: int


class UserReadWithRoles(UserRead):
    # 包含relationship的数据模型
    roles: List['Role'] = []


class UserRoles(SQLModel):
    roles: List['Role'] = []
    enable: List[str] = []


class User(UserBase, table=True):
    id: Optional[int] = Field(sa_column=Column('id', Integer, primary_key=True, autoincrement=True))
    roles: List['Role'] = Relationship(back_populates="users", link_model=UserRole)
    jobs: List['Job'] = Relationship(back_populates="user", link_model=UserJob)


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
