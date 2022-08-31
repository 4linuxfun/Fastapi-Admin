from typing import List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, Integer
from .relationships import MenuApis

if TYPE_CHECKING:
    from .menu import Menu


class ApiBase(SQLModel):
    tags: str = Field(max_length=10, sa_column_kwargs={'comment': '标签'})
    path: str = Field(max_length=50, sa_column_kwargs={'comment': 'API路径'})
    method: str = Field(max_length=10, sa_column_kwargs={'comment': 'HTTP方法'})
    summary: str = Field(max_length=20, sa_column_kwargs={'comment': '描述'})
    deprecated: bool = Field(default=False, sa_column_kwargs={'comment': '是否废弃'})


class Api(ApiBase, table=True):
    __tablename__ = 'sys_api'
    id: int = Field(sa_column=Column('id', Integer, primary_key=True, autoincrement=True))
    menus: List['Menu'] = Relationship(back_populates='apis', link_model=MenuApis)


class ApiWithMenus(ApiBase):
    id: int
    menus: List['Menu'] = []
