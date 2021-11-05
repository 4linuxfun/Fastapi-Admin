# coding: utf-8
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


# 这些是权限验证的基础表，单独放置
class RoleMenu(SQLModel, table=True):
    __tablename__ = "role_menu"
    role_id: int = Field(foreign_key="roles.id", primary_key=True)
    menu_id: int = Field(foreign_key="menu.id", primary_key=True)


class Menu(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    name: str
    path: str
    component: str
    type: Optional[str]
    parent_id: Optional[int]
    enable: int
    roles: List["Role"] = Relationship(back_populates="menus", link_model=RoleMenu)


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


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: Optional[str]
    password: Optional[str]
    enable: int
    avatar: Optional[str]
    email: Optional[str]
    roles: List['Role'] = Relationship(back_populates="users", link_model=UserRole)
