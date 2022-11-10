from typing import Union
from sqlmodel import select, Session
from ...models.internal.dictonary import DataDict, DictItem
from ..base import CRUDBase
from ...schemas.internal.user import UserInfo, UserLogin
from .roles import role


class CRUDDict(CRUDBase[DataDict]):
    pass


class CRUDItem(CRUDBase[DictItem]):
    pass


data_dict = CRUDDict(DataDict)
dict_item = CRUDItem(DictItem)
