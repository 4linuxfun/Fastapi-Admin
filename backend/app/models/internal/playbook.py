from typing import List, Union
from sqlmodel import SQLModel, Field, Column, Integer, String, TEXT


class Playbook(SQLModel, table=True):
    id: Union[int, None] = Field(default=None, sa_column=Column('id', Integer, primary_key=True, autoincrement=True))
    name: str = Field(sa_column=Column(String(50), nullable=False, comment='playbook名称'))
    playbook: str = Field(sa_column=Column(TEXT, nullable=False, comment='playbook文件'))
    desc: Union[str, None] = Field(default=None,
                                   sa_column=Column(String(255), default=None, nullable=True, comment='描述'))


class PlaybookSearch(SQLModel):
    name: Union[str, None] = None
