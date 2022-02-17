from typing import List
from pydantic import BaseModel
from models import Menu


class MenuApis(BaseModel):
    menu: Menu
    apis: List[str]
