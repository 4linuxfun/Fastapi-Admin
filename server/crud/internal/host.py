from typing import List, Optional, Dict, Union, Type
from loguru import logger
from pydantic import BaseModel
from sqlmodel import select, Session, or_

from ...models.internal import Pagination
from ...models.internal.host import Host, Group, HostGroup
from ..base import CRUDBase, JoinType
from ...settings import casbin_enforcer


class CRUDHost(CRUDBase[Host]):
    def search_total(self, session: Session, q: BaseModel, filter_type: Optional[Dict[str, str]] = None):
        pass

    def search(self, session: Session, search: Pagination, filter_type: Optional[Dict[str, str]] = None,
               columns: Optional[List] = None, order_col: Optional[str] = 'id',
               join_model: Union[Type[JoinType], None] = None):
        if columns is None:
            sql = select(self.model)
        else:
            sql = select(*columns)
        logger.debug(sql)
        # subquery查询找到order_col的起始值
        subquery = select(getattr(self.model, order_col))
        if join_model is not None:
            sql = sql.join(join_model, self.model.id == join_model.host_id)
            subquery = subquery.join(HostGroup, self.model.id == HostGroup.host_id)
            if search.search.group_id is not None:
                sql = sql.where(join_model.group_id == search.search.group_id)
                subquery = subquery.where(
                    HostGroup.group_id == search.search.group_id)
        logger.debug(subquery)
        subquery = self._make_search(subquery, search.search, filter_type)
        sql, subquery = self._make_pagination(sql, subquery, search, order_col)
        logger.debug(str(sql))
        results = session.exec(sql).all()
        return results


class CRUDGroup(CRUDBase[Group]):
    def search_groups(self, session: Session) -> List[Group]:
        sql = select(self.model)
        return session.exec(sql).all()


host = CRUDHost(Host)
group = CRUDGroup(Group)
