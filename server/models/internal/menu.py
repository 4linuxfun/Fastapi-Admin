from typing import Optional, List, Any, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, Boolean, Integer
from .relationships import RoleMenu, MenuApis


class MenuBase(SQLModel):
    id: Optional[int] = Field(sa_column=Column('id', Integer, primary_key=True, autoincrement=True))
    name: str = Field(max_length=20, sa_column_kwargs={'comment': '菜单名'})
    path: Optional[str] = Field(max_length=100, sa_column_kwargs={'comment': '路径'})
    component: Optional[str] = Field(max_length=50, sa_column_kwargs={'comment': '组件'})
    type: str = Field(max_length=10, sa_column_kwargs={'comment': '类型'})
    parent_id: Optional[int] = Field(sa_column_kwargs={'comment': '父级ID'})
    enable: bool = Field(default=True, sa_column=Column(Boolean, comment='启用'))


class Menu(MenuBase, table=True):
    roles: List["Role"] = Relationship(back_populates="menus", link_model=RoleMenu)
    apis: List['Api'] = Relationship(back_populates='menus', link_model=MenuApis)
    # apis: List['Api'] = Relationship(back_populates="menus", link_model=MenuApi)


class MenuRead(MenuBase):
    apis: List['Api'] = []


class MenusWithChild(MenuBase):
    apis: List['Api'] = []
    children: List['MenusWithChild'] = []


class MenuWithUpdate(MenuBase):
    # 更新菜单信息
    # id: Optional[int]
    apis: List[int] = []


# 底部导入，且延迟注释
from .role import Role
from .api import Api

MenusWithChild.update_forward_refs()
MenuRead.update_forward_refs()
