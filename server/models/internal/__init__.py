from .user import User
from .menu import Menu
from .role import Role, RoleMenu
from .dictonary import DataDict, DictItem
from .host import Host, Group
from .job import JobLogs
from .playbook import Playbook
from pydantic import BaseModel
from typing import TypeVar, Generic, Optional

T = TypeVar('T')


class Pagination(BaseModel, Generic[T]):
    search: T
    page: Optional[int] = 1
    page_size: Optional[int] = 10
    model: Optional[str] = 'asc'
