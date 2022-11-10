# 参考自：tiangolo/full-stack-fastapi-postgresql项目，部分代码为直接摘抄
from copy import deepcopy
from typing import TypeVar, Generic, List, Type, Any, Dict, Optional
from sqlmodel import Session, select, SQLModel, func, desc
from ..schemas.internal.pagination import Pagination

ModelType = TypeVar('ModelType', bound=SQLModel)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int):
        return db.exec(select(self.model).where(self.model.id == id)).one()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.exec(select(self.model).offset(skip).limit(limit)).all()

    def insert(self, db: Session, obj_in):
        # obj_in_data = jsonable_encoder(obj_in)
        # db_obj = self.model(**obj_in_data)
        db.add(obj_in)
        db.commit()
        db.refresh(obj_in)
        return obj_in

    def update(self, db: Session, db_obj, obj_in):
        # SQLModel直接使用的pydantic的dict方法，没有轮询SQLModel封装的__sqlmodel_relationships__，对于外键的更新，只能手动指定
        update_date = obj_in.dict()
        print(update_date)
        for field in update_date:
            setattr(db_obj, field, update_date[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int):
        obj = db.exec(select(self.model).where(self.model.id == id)).one()
        db.delete(obj)
        db.commit()
        return obj

    def _make_search(self, sql, search: Optional[Dict[str, Any]] = None, filter_type: Optional[Dict[str, str]] = None):
        """
        用于构建专用的sql查询语句，子类需要重写此方法
        :param sql:
        :param search:
        :param filter_type:指定的各属性值判断形式
        :return:
        """
        if search is None:
            return sql
        q = deepcopy(search)
        for key in q:
            print(f'check key is:{key}')
            if (key in filter_type.keys()) and (q[key] is not None):
                if filter_type[key] == 'l_like':
                    sql = sql.where(getattr(self.model, key).like(f'%{q[key]}'))
                elif filter_type[key] == 'r_like':
                    sql = sql.where(getattr(self.model, key).like(f'{q[key]}%'))
                elif filter_type[key] == 'like':
                    sql = sql.where(getattr(self.model, key).like(f'%{q[key]}%'))
                elif filter_type[key] == 'eq':
                    sql = sql.where(getattr(self.model, key) == q[key])
                elif filter_type[key] == 'ne':
                    sql = sql.where(getattr(self.model, key) != q[key])
                elif filter_type[key] == 'lt':
                    sql = sql.where(getattr(self.model, key) < q[key])
                elif filter_type[key] == 'le':
                    sql = sql.where(getattr(self.model, key) <= q[key])
                elif filter_type[key] == 'gt':
                    sql = sql.where(getattr(self.model, key) > q[key])
                elif filter_type[key] == 'ge':
                    sql = sql.where(getattr(self.model, key) >= q[key])
                elif filter_type[key] == 'bool':
                    key_value = 1 if q[key] else 0
                    sql = sql.where(getattr(self.model, key) == key_value)
        return sql

    def search(self, session: Session, search: Pagination, filter_type: Optional[Dict[str, str]] = None,
               columns: Optional[List] = None):
        """
        分页查询方法
        :param session:
        :param search: Pagination实例对象，包含各搜索参数
        :param filter_type: 指定的各属性值判断形式
        :param columns: 查询返回指定columns
        :return:
        """
        if columns is None:
            sql = select(self.model)
        else:
            sql = select(*columns)
        sql = self._make_search(sql, search.search, filter_type)
        subquery = select(self.model.id)
        subquery = self._make_search(subquery, search.search, filter_type)
        if search.model == 'desc':
            subquery = subquery.order_by(desc(self.model.id))
        else:
            subquery = subquery.order_by(self.model.id)
        subquery = subquery.offset(
            (search.page - 1) * search.page_size).limit(1).subquery()
        if search.model == 'desc':
            sql = sql.where(self.model.id <= subquery).order_by(desc(self.model.id)).limit(search.page_size)
        else:
            sql = sql.where(self.model.id >= subquery).limit(search.page_size)
        print(sql)
        results = session.exec(sql).all()
        return results

    def search_total(self, session: Session, q: Dict[str, Any], filter_type: Optional[Dict[str, str]] = None):
        """
        每次进行分页查询的时候，都需要返回一个total值，表示对应搜索，现阶段数据库有多少内容，便于前端分页数
        :param session:
        :param q:
        :param filter_type: 字段过滤形式
        :return:
        """
        sql = select(func.count(self.model.id))
        sql = self._make_search(sql, q, filter_type)
        return session.execute(sql).scalar()
