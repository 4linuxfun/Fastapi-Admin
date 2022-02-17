from typing import List
from pydantic import BaseModel
from ..models import Role


class RoleInfo(BaseModel):
    role: Role
    menus: List[int]
    category: List[int]
