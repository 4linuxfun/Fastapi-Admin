from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Field, JSON, Column, Relationship
from sqlalchemy.ext.mutable import MutableDict


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


class CategoryField(SQLModel, table=True):
    # 资产表字段对应关系
    __tablename__ = 'category_field'
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
    alias: Optional[str]
    desc: Optional[str]
    type: Optional[str]
    need: Optional[int]
    multi: Optional[int]
    show: Optional[int]
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category: List[Category] = Relationship(back_populates="fields")


class Assets(SQLModel, table=True):
    # 资产表
    id: Optional[int] = Field(default=None, primary_key=True)
    category: Optional[str]
    user: Optional[str]
    manager: Optional[str]
    area: Optional[str]
    info: Optional[Dict[Any, Any]] = Field(default=None, sa_column=Column(MutableDict.as_mutable(JSON)))
    deleted: Optional[int] = 0
