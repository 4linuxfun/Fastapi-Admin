from typing import List
from pydantic import BaseModel
from ..models import Category, CategoryField


class UpdateCategory(BaseModel):
    category: Category
    fields: List[CategoryField]
