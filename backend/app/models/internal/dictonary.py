from typing import Optional, List, Union
from sqlmodel import SQLModel, Field, Relationship, Column, Boolean, Integer, String


class DataDictBase(SQLModel):
    name: str = Field(sa_column=Column(String(50), nullable=False, comment='字典名称'))
    code: str = Field(sa_column=Column(String(100), nullable=False, comment='字典编号'))
    desc: Optional[str] = Field(sa_column=Column(String(100), default=None, comment='描述'))


class DataDict(DataDictBase, table=True):
    __tablename__ = 'data_dict'
    id: Optional[int] = Field(sa_column=Column('id', Integer, primary_key=True, autoincrement=True))
    dict_items: List["DictItem"] = Relationship(back_populates="dict")


class DataDictSearch(SQLModel):
    name: Optional[str]
    code: Optional[str]


class DictBase(SQLModel):
    label: str = Field(sa_column=Column(String(50), nullable=False, comment='名称'))
    value: str = Field(sa_column=Column(String(100), nullable=False, comment='数据值'))
    desc: Optional[str] = Field(sa_column=Column(String(100), default=None, comment='描述'))
    sort: Optional[int] = Field(sa_column=Column(Integer, default=1, comment='排序值，越小越靠前'))
    enable: bool = Field(sa_column=Column(Boolean, default=True, comment='是否启用'))
    dict_id: Optional[int] = Field(foreign_key="data_dict.id")


class DictItem(DictBase, table=True):
    __tablename__ = 'dict_item'

    id: Optional[int] = Field(sa_column=Column('id', Integer, primary_key=True, autoincrement=True))
    dict: Optional[DataDict] = Relationship(back_populates='dict_items')


class DictRead(DictBase):
    id: int


class DictUpdate(DictBase):
    id: Optional[int]


class DictItemSearch(SQLModel):
    dict_id: int
    name: Union[str, None] = None
    data: Union[str, None] = None
    enable: Union[bool, None] = None


class DictItemSearchFilter(SQLModel):
    dict_id: str
    label: str
    value: str
    enable: str
