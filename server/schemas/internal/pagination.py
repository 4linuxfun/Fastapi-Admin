from typing import Optional, Generic, TypeVar, Dict
from pydantic import BaseModel

T = TypeVar('T')


class Pagination(BaseModel, Generic[T]):
    search: T
    page: Optional[int] = 1
    page_size: Optional[int] = 10
    model: Optional[str] = 'asc'


class SearchBase(BaseModel):
    type: Dict[str, str]
