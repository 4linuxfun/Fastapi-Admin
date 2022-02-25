from .assets import System, Category, CategoryField, ShareFields, Assets
from .menu import Menu
from .role import Role
from .user import User
from .api import Api
from .relationships import RoleMenu, RoleCategory, UserRole

#
# class Permission(SQLModel, table=True):
#     __tablename__ = "casbin_rule"
#     id: Optional[int] = Field(default=None, primary_key=True)
#     ptype: Optional[str]
#     v0: Optional[str]
#     v1: Optional[str]
#     v2: Optional[str]
#     v3: Optional[str]
#     v4: Optional[str]
#     v5: Optional[str]
