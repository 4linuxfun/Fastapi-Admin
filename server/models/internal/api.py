from typing import List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from .relationships import MenuApis

if TYPE_CHECKING:
    from .menu import Menu


class ApiBase(SQLModel):
    tags: str
    path: str
    method: str
    summary: str
    deprecated: int = Field(default=0)


class Api(ApiBase, table=True):
    __tablename__ = 'sys_api'
    id: int = Field(default=None, primary_key=True)
    menus: List['Menu'] = Relationship(back_populates='apis', link_model=MenuApis)


class ApiWithMenus(ApiBase):
    id: int
    menus: List['Menu'] = []
