from typing import Optional, List, Any, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from .relationships import RoleMenu, MenuApis


class MenuBase(SQLModel):
    name: Optional[str]
    path: Optional[str]
    component: Optional[str]
    type: Optional[str]
    parent_id: Optional[int]
    enable: int


class Menu(MenuBase, table=True):
    id: Optional[int] = Field(primary_key=True)
    roles: List["Role"] = Relationship(back_populates="menus", link_model=RoleMenu)
    apis: List['Api'] = Relationship(back_populates='menus', link_model=MenuApis)
    # apis: List['Api'] = Relationship(back_populates="menus", link_model=MenuApi)


class MenuRead(MenuBase):
    id: int
    apis: List['Api'] = []


class MenusWithChild(MenuBase):
    id: int
    apis: List['Api'] = []
    children: List['MenusWithChild'] = []


class MenuWithUpdate(MenuBase):
    # 更新菜单信息
    id: int
    apis: List[int] = []


# 底部导入，且延迟注释
from .role import Role
from .api import Api

MenusWithChild.update_forward_refs()
MenuRead.update_forward_refs()
