from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from .relationships import RoleMenu, UserRole, RoleCategory

if TYPE_CHECKING:
    from .user import User
    from .menu import Menu
    from .assets import Category


class Role(SQLModel, table=True):
    __tablename__ = "roles"
    id: int = Field(default=None, primary_key=True)
    name: str = Field(..., title="角色", description="请输入角色名")
    description: str
    enable: int
    menus: List["Menu"] = Relationship(back_populates="roles", link_model=RoleMenu)
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRole)
    category: List["Category"] = Relationship(back_populates="roles", link_model=RoleCategory)
