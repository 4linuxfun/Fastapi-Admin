from sqlmodel import SQLModel, Field


# 这些是权限验证的基础表，单独放置
class RoleMenu(SQLModel, table=True):
    __tablename__ = "role_menu"
    role_id: int = Field(foreign_key="roles.id", primary_key=True)
    menu_id: int = Field(foreign_key="menu.id", primary_key=True)


class UserRole(SQLModel, table=True):
    __tablename__ = 'user_roles'

    user_id: int = Field(foreign_key="user.id", primary_key=True)
    role_id: int = Field(foreign_key="roles.id", primary_key=True)


class MenuApis(SQLModel, table=True):
    __tablename__ = 'menu_apis'
    menu_id: int = Field(foreign_key='menu.id', primary_key=True)
    api_id: int = Field(foreign_key='sys_api.id', primary_key=True)
