from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Column, Boolean, Integer
from .relationships import RoleMenu


class MenuBase(SQLModel):
    id: Optional[int] = Field(sa_column=Column('id', Integer, primary_key=True, autoincrement=True))
    name: str = Field(max_length=20, sa_column_kwargs={'comment': '菜单名'})
    path: Optional[str] = Field(max_length=100, sa_column_kwargs={'comment': '路径'})
    component: Optional[str] = Field(max_length=50, sa_column_kwargs={'comment': '组件'})
    auth: Optional[str] = Field(max_length=50, sa_column_kwargs={'comment': '授权标识'})
    type: str = Field(max_length=10, sa_column_kwargs={'comment': '类型'})
    parent_id: Optional[int] = Field(sa_column_kwargs={'comment': '父级ID'})
    sort: Optional[float] = Field(sa_column_kwargs={'comment': '菜单排序'})
    enable: bool = Field(default=True, sa_column=Column(Boolean, comment='启用'))


class Menu(MenuBase, table=True):
    roles: List["Role"] = Relationship(back_populates="menus", link_model=RoleMenu)
    # apis: List['Api'] = Relationship(back_populates="menus", link_model=MenuApi)


class MenusWithChild(MenuBase):
    children: List['MenusWithChild'] = []


# 底部导入，且延迟注释
from .role import Role

MenusWithChild.update_forward_refs()
