from typing import Optional, List, Literal, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from .relationships import UserRole
from .role import Role

if TYPE_CHECKING:
    from .role import Role


class UserBase(SQLModel):
    name: Optional[str]
    password: Optional[str]
    enable: int
    avatar: Optional[str] = Field(..., title='头像')
    email: Optional[str] = Field(..., title='邮箱', )
    # age: Optional[int] = Field(..., title='年龄', lt=120)


class UserRead(UserBase):
    # get请求时返回的数据模型，response_model使用模型
    id: int


class UserCreate(UserBase):
    # POST请求时，传递过来的模型
    class Config:
        title = '新建用户'


class UserReadWithRoles(UserRead):
    # 包含relationship的数据模型
    roles: List['Role'] = []


class UserRoles(SQLModel):
    roles: List['Role'] = []
    enable: List[str] = []


class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    roles: List['Role'] = Relationship(back_populates="users", link_model=UserRole)


class UserUpdateWithRoles(SQLModel):
    # PUT请求时，传递过来的数据模型
    user: User
    roles: List[int]


class UserInfo(SQLModel):
    user: UserCreate
    roles: Role

    # dep: Dep

    class Config:
        title = '用户信息显示'


class UserLogin(SQLModel):
    username: str
    password: str


class LoginResponse(SQLModel):
    uid: int
    token: str
