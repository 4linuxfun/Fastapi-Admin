from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from .relationships import RoleMenu

if TYPE_CHECKING:
    from .role import Role


class Menu(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    name: Optional[str]
    path: Optional[str]
    component: Optional[str]
    api: Optional[str]
    type: Optional[str]
    parent_id: Optional[int]
    enable: int
    url: Optional[str]
    roles: List["Role"] = Relationship(back_populates="menus", link_model=RoleMenu)
    # apis: List['Api'] = Relationship(back_populates="menus", link_model=MenuApi)
