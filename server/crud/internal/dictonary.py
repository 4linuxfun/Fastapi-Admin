from typing import Optional, List, Dict
from loguru import logger
from sqlmodel import select, Session, desc
from ...models.internal.dictonary import DataDict, DictItem, DictItemSearch
from ..base import CRUDBase
from ...schemas.internal.pagination import Pagination


class CRUDDict(CRUDBase[DataDict]):
    pass


class CRUDItem(CRUDBase[DictItem]):
    def get_items_by_code(self, db: Session, code: str):
        dict_id = select(DataDict.id).where(DataDict.code == code).subquery()
        sql = select(self.model).where(self.model.dict_id == dict_id).where(self.model.enable == 1).order_by(
            self.model.sort)
        return db.exec(sql).all()

    def search(self, session: Session, search: Pagination[DictItemSearch], filter_type: Optional[Dict[str, str]] = None,
               columns: Optional[List] = None, order_col: Optional[str] = 'id'):
        """
        重写search函数，数据字典通过sort进行排序
        """
        sql = select(self.model).where(self.model.dict_id == search.search['dict_id'])
        sql = self._make_search(sql, search.search, filter_type)
        if search.model == 'desc':
            sql = sql.order_by(desc(self.model.sort))
        else:
            sql = sql.order_by(self.model.sort)
        sql = sql.limit(search.page_size).offset((search.page - 1) * search.page_size)
        logger.debug(sql)
        return session.exec(sql).all()


data_dict = CRUDDict(DataDict)
dict_item = CRUDItem(DictItem)
