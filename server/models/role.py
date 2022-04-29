from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from .relationships import RoleMenu, UserRole

if TYPE_CHECKING:
    from .user import User
    from .menu import Menu


class RoleBase(SQLModel):
    name: str = Field(..., title="角色", description="请输入角色名")
    description: str
    enable: int


class Role(RoleBase, table=True):
    __tablename__ = "roles"
    id: int = Field(default=None, primary_key=True)
    menus: List["Menu"] = Relationship(back_populates="roles", link_model=RoleMenu)
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRole)


class RoleUpdate(RoleBase):
    id: int
    menus: List[int]


class RoleWithMenus(RoleBase):
    id: int
    menus: List['Menu'] = []


from .menu import Menu

RoleWithMenus.update_forward_refs()
