from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from .relationships import UserRole

if TYPE_CHECKING:
    from .role import Role


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: Optional[str] = Field(..., title="用户名", description="请输入用户名")
    password: Optional[str]
    enable: int
    avatar: Optional[str]
    email: Optional[str]
    roles: List['Role'] = Relationship(back_populates="users", link_model=UserRole)
