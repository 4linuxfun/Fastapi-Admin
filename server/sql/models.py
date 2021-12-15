# coding: utf-8
from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Field, JSON, Column, Relationship
from sqlalchemy.ext.mutable import MutableDict


# 这些是权限验证的基础表，单独放置
class RoleMenu(SQLModel, table=True):
    __tablename__ = "role_menu"
    role_id: int = Field(foreign_key="roles.id", primary_key=True)
    menu_id: int = Field(foreign_key="menu.id", primary_key=True)


class RoleCategory(SQLModel, table=True):
    __tablename__ = 'role_category'
    role_id: int = Field(foreign_key="roles.id", primary_key=True)
    category_id: int = Field(foreign_key="category.id", primary_key=True)


class MenuApi(SQLModel, table=True):
    __tablename__ = "menu_api"
    menu_id: Optional[int] = Field(default=None, foreign_key="menu.id", primary_key=True)
    api_id: Optional[int] = Field(default=None, foreign_key="sys_api.id", primary_key=True)


class Menu(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    name: Optional[str]
    path: Optional[str]
    component: Optional[str]
    type: Optional[str]
    parent_id: Optional[int]
    enable: int
    url: Optional[str]
    roles: List["Role"] = Relationship(back_populates="menus", link_model=RoleMenu)
    apis: List['Api'] = Relationship(back_populates="menus", link_model=MenuApi)


class UserRole(SQLModel, table=True):
    __tablename__ = 'user_roles'

    user_id: int = Field(foreign_key="user.id", primary_key=True)
    role_id: int = Field(foreign_key="roles.id", primary_key=True)


class Role(SQLModel, table=True):
    __tablename__ = "roles"
    id: int = Field(default=None, primary_key=True)
    name: str
    description: str
    enable: int
    menus: List["Menu"] = Relationship(back_populates="roles", link_model=RoleMenu)
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRole)
    category: List["Category"] = Relationship(back_populates="roles", link_model=RoleCategory)


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: Optional[str]
    password: Optional[str]
    enable: int
    avatar: Optional[str]
    email: Optional[str]
    roles: List['Role'] = Relationship(back_populates="users", link_model=UserRole)


class Api(SQLModel, table=True):
    __tablename__ = "sys_api"
    id: int = Field(default=None, primary_key=True)
    name: Optional[str]
    path: Optional[str]
    enable: int
    menus: List[Menu] = Relationship(back_populates="apis", link_model=MenuApi)


# 资产相关的表定义


class System(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    host: Optional[str]
    ip: Optional[str]
    system: Optional[str]
    storage: Optional[int]
    memory: Optional[int]
    cpu: Optional[int]
    admin: Optional[str]
    env: Optional[str]
    type: Optional[str]
    project: Optional[str]
    developer: Optional[str]
    info: Optional[Dict[Any, Any]] = Field(default=None, sa_column=Column(JSON))


class Category(SQLModel, table=True):
    # 资产表描述
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
    alias: Optional[str]
    desc: Optional[str]
    fields: List["CategoryField"] = Relationship(back_populates="category")
    roles: List[Role] = Relationship(back_populates="category", link_model=RoleCategory)


class CategoryField(SQLModel, table=True):
    # 资产表字段对应关系
    __tablename__ = 'category_field'
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
    desc: Optional[str]
    type: Optional[str]
    need: Optional[int]
    multi: Optional[int]
    show: Optional[int]
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category: List[Category] = Relationship(back_populates="fields")


class ShareFields(SQLModel):
    """
    资产列表的固定通用字段统一设定
    """
    category: Optional[str]
    user: Optional[str]
    manager: Optional[str]
    area: Optional[str]

    @classmethod
    def share_names(cls, ):
        """
        需要维护一个共用字段的映射关系
        :return:
        """
        return {'category': '资产类型',
                'user': '使用人',
                'manager': '管理员',
                'area': "区域"}


class Assets(ShareFields, table=True):
    # 资产表
    id: Optional[int] = Field(default=None, primary_key=True)
    info: Optional[Dict[Any, Any]] = Field(default=None, sa_column=Column(MutableDict.as_mutable(JSON)))
    deleted: Optional[int] = 0
