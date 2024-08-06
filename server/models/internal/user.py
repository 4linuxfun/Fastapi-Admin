from typing import Optional, List, Union, Literal, TYPE_CHECKING
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship, Column, Integer, Boolean, String
from .relationships import UserRole
from .role import Role

if TYPE_CHECKING:
    from .role import Role
    from .job import Job


class User(SQLModel, table=True):
    __tablename__ = 'user'
    id: Optional[int] = Field(sa_column=Column('id', Integer, primary_key=True, autoincrement=True))
    name: Union[str, None] = Field(sa_column=Column(String(20), nullable=False, unique=True, comment='用户名'))
    enable: Union[bool, None] = Field(sa_column=Column(Boolean, default=True, comment='可用'))
    avatar: Union[str, None] = Field(sa_column=Column(String(100), default=None, comment='头像'))
    email: Union[str, None] = Field(sa_column=Column(String(20), default=None, comment='邮箱'))
    password: Optional[str] = Field(sa_column=Column(String(50), comment='密码'))
    roles: List['Role'] = Relationship(back_populates="users", link_model=UserRole)


class UserWithOutPasswd(SQLModel):
    name: Union[str, None] = Field(max_length=20, nullable=False)
    enable: Union[bool, None] = Field(default=True)
    avatar: Union[str, None] = Field(max_length=100, default=None)
    email: Union[str, None] = Field(max_length=20, default=None)


class UserBase(UserWithOutPasswd):
    password: Optional[str] = Field(sa_column=Column(String(50), comment='密码'))
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


class UserInfo(BaseModel):
    user: User
    roles: List[str]
