from typing import Optional
from sqlmodel import SQLModel, Field


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
