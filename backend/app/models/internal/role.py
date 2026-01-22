from typing import Optional, List, TYPE_CHECKING, Union
from sqlmodel import SQLModel, Field, Relationship, Column, Integer, Boolean, String
from .relationships import RoleMenu, UserRole

if TYPE_CHECKING:
    from .user import User
    from .menu import Menu


class Role(SQLModel, table=True):
    __tablename__ = "roles"
    id: Optional[int] = Field(sa_column=Column('id', Integer, primary_key=True, autoincrement=True))
    name: Union[str, None] = Field(sa_column=Column(String(20), nullable=False, unique=True, comment='角色名'))
    description: Union[str, None] = Field(sa_column=Column(String(100), default=None, comment='描述'))
    enable: Union[bool, None] = Field(sa_column=Column(Boolean, default=True, comment='启用'))
    menus: List["Menu"] = Relationship(back_populates="roles", link_model=RoleMenu)
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRole)


class RoleBase(SQLModel):
    name: Union[str, None] = Field(max_length=20, nullable=False)
    description: Union[str, None] = Field(max_length=100, default=None)
    enable: Union[bool, None] = Field(default=True)


class RoleInsert(RoleBase):
    menus: List[int]


class RoleUpdate(RoleInsert):
    id: int


class RoleWithMenus(RoleBase):
    id: int
    menus: List['Menu'] = []


from .menu import Menu

RoleWithMenus.model_rebuild()
