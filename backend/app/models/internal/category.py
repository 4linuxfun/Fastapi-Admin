from sqlmodel import SQLModel, Column, Integer, String, Boolean, Field, Relationship, Date, DateTime
from sqlmodel import func
from typing import List, Optional, Union
from datetime import datetime, date


class Category(SQLModel, table=True):
    # 分类字典表
    __tablename__ = 'category'
    id: Optional[int] = Field(sa_column=Column(
        'id', Integer, primary_key=True, autoincrement=True))
    name: Union[str, None] = Field(sa_column=Column(
        String(100), nullable=False, unique=True, comment='分类名称'))
    code: Union[str, None] = Field(sa_column=Column(
        String(100), comment='分类编码'))
    parent_id: Union[int, None] = Field(sa_column=Column(
        Integer, comment='父级ID'))
    is_deleted: Union[bool, None] = Field(sa_column=Column(
        Boolean, default=False, comment='是否删除'))


class CategoryWithChild(SQLModel):
    id: Union[int, None]
    name: Union[str, None]
    code: Union[str, None]
    children: List['CategoryWithChild'] = []


CategoryWithChild.model_rebuild()
