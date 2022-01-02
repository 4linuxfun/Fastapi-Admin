from typing import List
from pydantic import BaseModel
from ..sql.models import Menu


class MenuApis(BaseModel):
    menu: Menu
    apis: List[str]
