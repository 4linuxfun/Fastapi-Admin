from typing import Union
from sqlmodel import select, Session
from ...models.internal.dictonary import DataDict, DictItem
from ..base import CRUDBase
from ...schemas.internal.user import UserInfo, UserLogin
from .roles import role


class CRUDDict(CRUDBase[DataDict]):
    pass


class CRUDItem(CRUDBase[DictItem]):
    def get_items_by_code(self, db: Session, code: str):
        dict_id = select(DataDict.id).where(DataDict.code == code).subquery()
        sql = select(self.model).where(self.model.dict_id == dict_id).where(self.model.enable == 1).order_by(
            self.model.id)
        return db.exec(sql).all()


data_dict = CRUDDict(DataDict)
dict_item = CRUDItem(DictItem)
