from typing import TypeVar, Generic
from pydantic import BaseModel
from .pagination import SearchBase
from ...models.internal.dictonary import DataDict, DictItem, DictBase


class DictSearch(DataDict, SearchBase):
    pass


class DictItemSearch(DictItem, SearchBase):
    pass


class DictItem(DictBase):
    dict_id: int
