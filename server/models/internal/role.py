from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, Integer, Boolean
from .relationships import RoleMenu, UserRole

if TYPE_CHECKING:
    from .user import User
    from .menu import Menu


class RoleBase(SQLModel):
    name: str = Field(max_length=20, sa_column_kwargs={'comment': '角色名'})
    description: str = Field(max_length=100, sa_column_kwargs={'comment': '描述'})
    enable: bool = Field(default=True, sa_column=Column(Boolean, comment='启用'))


class Role(RoleBase, table=True):
    __tablename__ = "roles"
    id: Optional[int] = Field(sa_column=Column('id', Integer, primary_key=True, autoincrement=True))
    menus: List["Menu"] = Relationship(back_populates="roles", link_model=RoleMenu)
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRole)


class RoleInsert(RoleBase):
    menus: List[int]


class RoleUpdate(RoleInsert):
    id: int


class RoleWithMenus(RoleBase):
    id: int
    menus: List['Menu'] = []


from .menu import Menu

RoleWithMenus.update_forward_refs()
