from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Column, Boolean, Integer, String, Float
from .relationships import RoleMenu


class MenuBase(SQLModel):
    id: Optional[int] = Field(sa_column=Column('id', Integer, primary_key=True, autoincrement=True))
    name: str = Field(sa_column=Column(String(20), nullable=False, comment='菜单名'))
    icon: Optional[str] = Field(default=None, sa_column=Column(String(50), default=None, comment='Icon图标'))
    path: Optional[str] = Field(sa_column=Column(String(100), default=None, comment='路径'))
    component: Optional[str] = Field(sa_column=Column(String(50), default=None, comment='组件'))
    auth: Optional[str] = Field(sa_column=Column(String(50), default=None, comment='授权标识'))
    type: str = Field(sa_column=Column(String(10), nullable=False, comment='类型'))
    parent_id: Optional[int] = Field(sa_column=Column(Integer, default=None, comment='父级ID'))
    sort: Optional[float] = Field(default=None, sa_column=Column(Float, default=None, comment='菜单排序'))
    enable: bool = Field(sa_column=Column(Boolean, default=True, comment='启用'))


class Menu(MenuBase, table=True):
    roles: List["Role"] = Relationship(back_populates="menus", link_model=RoleMenu)
    # apis: List['Api'] = Relationship(back_populates="menus", link_model=MenuApi)


class MenusWithChild(MenuBase):
    children: List['MenusWithChild'] = []


# 底部导入，且延迟注释
from .role import Role

MenusWithChild.model_rebuild()
