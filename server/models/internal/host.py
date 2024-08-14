from typing import List, Union
from sqlmodel import SQLModel, Field, Column, Text, Integer, String, Relationship


class HostGroup(SQLModel, table=True):
    """
    通过中间表实现：主机-组的对应关系
    """
    __tablename__ = 'host_group'
    host_id: int = Field(foreign_key="host.id", primary_key=True, nullable=False)
    group_id: int = Field(foreign_key="group.id", primary_key=True, nullable=False)


class Host(SQLModel, table=True):
    __tablename__ = 'host'
    id: int = Field(sa_column=Column('id', Integer, primary_key=True, autoincrement=True))
    name: str = Field(sa_column=Column(String(50), unique=True, nullable=False, comment='主机名'))
    ansible_host: str = Field(sa_column=Column(String(50), nullable=False, comment='主机地址'))
    ansible_port: int = Field(sa_column=Column(Integer, default=22, nullable=False, comment='ssh端口'))
    ansible_user: str = Field(sa_column=Column(String(50), nullable=True, default=None, comment='ssh用户名'))
    ansible_password: str = Field(sa_column=Column(String(50), default=None, comment='ssh密码'))
    ansible_ssh_private_key: str = Field(
        sa_column=Column('ansible_ssh_private_key', Text, default=None, nullable=True, comment='私钥'))
    desc: str = Field(sa_column=Column(String(100), default=None, nullable=True, comment='描述'))
    groups: List['Group'] = Relationship(back_populates='hosts', link_model=HostGroup)


class Group(SQLModel, table=True):
    __tablename__ = 'group'
    id: int = Field(sa_column=Column('id', Integer, primary_key=True, autoincrement=True))
    name: str = Field(sa_column=Column(String(50), nullable=False, comment='组名'))
    parent_id: int = Field(sa_column=Column(Integer, default=None, nullable=True, comment='父ID'))
    ancestors: Union[str, None] = Field(
        sa_column=Column(String(100), default=None, nullable=True, comment='祖先ID列表'))
    hosts: List['Host'] = Relationship(back_populates='groups', link_model=HostGroup)


class GroupWithChild(SQLModel):
    id: int
    name: str
    parent_id: Union[int, None]
    ancestors: Union[str, None]
    children: List['GroupWithChild'] = []


class CreateHost(SQLModel):
    id: Union[int, None] = None
    name: str
    groups: List[int]
    ansible_host: str
    ansible_port: int
    ansible_user: str
    ansible_password: Union[str, None] = None
    ansible_ssh_private_key: Union[str, None]
    desc: Union[str, None]


class HostWithIp(SQLModel):
    name: Union[str, None] = None
    ansible_host: Union[str, None] = None
    group_id: Union[int, None] = None
    ancestors: Union[str, None]
