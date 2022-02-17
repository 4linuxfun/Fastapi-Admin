from typing import List, Union, Any
from sqlmodel import select, Session, func
from ..models import Assets
from ..schemas.assets import SearchForm
from .base import CRUDBase


class CRUDAssets(CRUDBase[Assets]):
    def get_search_count(self, session: Session, q: str):
        pass

    def search_total(self, session: Session, search: SearchForm):
        sql = self.make_search_sql(search, model='count')
        return session.execute(sql).scalar()

    def search_assets(self, session: Session, search: SearchForm):
        sql = self.make_search_sql(search)
        sql = sql.offset(search.offset).limit(search.limit)
        print(str(sql))
        return session.exec(sql).all()

    def make_search_sql(self, search: SearchForm, model='all') -> Union[List[Assets], Any]:
        """
        searchForm生成对应的查询sql
        :param search:
        :param model: 'all':代表查询所有，'count':表示返回count
        :return:
        """
        if model == 'all':
            sql = select(self.model)
        elif model == 'count':
            sql = select(func.count(self.model.id))
        if search.category:
            sql = sql.where(self.model.category.like('%' + search.category + '%'))
        if search.manager:
            sql = sql.where(self.model.manager.like('%' + search.manager + '%'))
        if search.area:
            sql = sql.where(self.model.area.like('%' + search.area + '%'))
        if search.user:
            sql = sql.where(self.model.user.like('%' + search.user + '%'))
        if search.filters is not None:
            for filter in search.filters:
                print(filter)
                if filter['field'] is None:
                    continue
                if filter['mode'] == 'like':
                    sql = sql.where(self.model.info[filter['field']].like('%' + filter['value'] + '%'))
                if filter['mode'] == 'eq':
                    sql = sql.where(self.model.info[filter['field']] == filter['value'])
                if filter['mode'] == 'lt':
                    sql = sql.where(self.model.info[filter['field']] < filter['value'])
                if filter['mode'] == 'le':
                    sql = sql.where(self.model.info[filter['field']] <= filter['value'])
                if filter['mode'] == 'gt':
                    sql = sql.where(self.model.info[filter['field']] > filter['value'])
                if filter['mode'] == 'ge':
                    sql = sql.where(self.model.info[filter['field']] >= filter['value'])
                if filter['mode'] == 'ne':
                    sql = sql.where(self.model.info[filter['field']] != filter['value'])
        return sql


assets = CRUDAssets(Assets)
