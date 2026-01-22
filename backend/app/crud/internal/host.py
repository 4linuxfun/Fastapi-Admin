from typing import List, Optional, Dict, Union, Type

import sqlalchemy.orm.exc
from loguru import logger
from pydantic import BaseModel
from sqlmodel import select, Session, func

from ...models.internal import Pagination
from ...models.internal.host import Host, Group, HostGroup
from ..base import CRUDBase


class CRUDHost(CRUDBase[Host]):
    def _host_search(self, sql, q: BaseModel):
        """
        构建主机查询语句，返回sql
        """
        logger.debug(q)
        sql = sql.join(HostGroup, self.model.id == HostGroup.host_id)
        if q.name is not None:
            sql = sql.where(self.model.name.like('%' + q.name + '%'))
        if q.ansible_host is not None:
            sql = sql.where(self.model.ansible_host.like('%' + q.ansible_host + '%'))
        if q.group_id is not None:
            sub_query1 = select(Group.id).where(Group.id == q.group_id)
            if q.ancestors is None:
                sub_query2 = select(Group.id).where(Group.ancestors.like(q.ancestors + ',' + str(q.group_id) + ',%'))
            else:
                sub_query2 = select(Group.id).where(Group.ancestors.like(str(q.group_id)))
            sql = sql.where(HostGroup.group_id.in_(sub_query1.union_all(sub_query2)))

        sql = sql.group_by(self.model.id).order_by(self.model.id)
        return sql

    def search_total(self, session: Session, q: BaseModel, filter_type: Optional[Dict[str, str]] = None):
        sql = select(self.model)
        sql = self._host_search(sql, q)
        sql = sql.subquery()
        count_sql = select(func.count(sql.c.id)).select_from(sql)
        logger.debug(count_sql)
        try:
            result = session.exec(count_sql).one()
        except sqlalchemy.orm.exc.NoResultFound:
            result = 0
        logger.debug(result)
        return result

    def search(self, session: Session, search: Pagination, filter_type: Optional[Dict[str, str]] = None,
               columns: Optional[List] = None, order_col: Optional[str] = 'id'):
        """
        实现主机管理界面的分页查询
        """
        sql = select(self.model)
        sql = self._host_search(sql, search.search)
        sql = sql.limit(search.page_size).offset((search.page - 1) * search.page_size)
        logger.debug(sql)
        results = session.exec(sql).all()
        logger.debug(results)
        return results


class CRUDGroup(CRUDBase[Group]):
    def search_groups(self, session: Session) -> List[Group]:
        sql = select(self.model)
        return session.exec(sql).all()


host = CRUDHost(Host)
group = CRUDGroup(Group)
