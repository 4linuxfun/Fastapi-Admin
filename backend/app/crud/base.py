# 参考自：tiangolo/full-stack-fastapi-postgresql项目，部分代码为直接摘抄
from copy import deepcopy
from loguru import logger
from pydantic import BaseModel
from typing import TypeVar, Generic, List, Type, Any, Dict, Optional, Union
from sqlmodel import Session, select, SQLModel, func, desc, join, delete
from sqlalchemy.orm.exc import NoResultFound
from ..models.internal import Pagination

ModelType = TypeVar('ModelType', bound=SQLModel)
JoinType = TypeVar('JoinType', bound=SQLModel)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int):
        return db.exec(select(self.model).where(self.model.id == id)).one()

    def get_by_colume(self, db: Session, search: Dict[str, Any], filter: Dict[str, str] | None = {'id': 'eq'}):
        """
        通过指定列查询,且需要传入匹配模式，filter: {'name','like'},可为：l_like,r_like,like,eq,ne,lt,le,gt,ge,in
        默认查询id相等的行
        :param db:
        :param search: 查询内容：{'name':123}
        :param filter:
        :return:
        """
        sql = select(self.model)
        sql = self._make_search(sql, search, filter)
        return db.exec(sql).all()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.exec(select(self.model).offset(skip).limit(limit)).all()

    def get_all(self, db: Session):
        return db.exec(select(self.model)).all()

    def get_multi_by_ids(self, db: Session, ids: List[int]) -> List[ModelType]:
        """
        通过数组id列表清单，查找符合的数据
        """
        return db.exec(select(self.model).where(self.model.id.in_(ids))).all()

    def insert(self, db: Session, obj_in):
        # obj_in_data = jsonable_encoder(obj_in)
        # db_obj = self.model(**obj_in_data)
        db.add(obj_in)
        # db.commit()
        db.flush()
        return obj_in

    def update(self, db: Session, db_obj: ModelType, new_obj: ModelType):
        """
        使用sqlmodel新函数sqlmodel_update更新
        :param db:
        :param db_obj:
        :param new_obj:
        """
        update_date = new_obj.model_dump(exclude_unset=True)
        logger.debug(update_date)
        db_obj.sqlmodel_update(update_date)
        db.add(db_obj)
        db.flush()
        return db_obj

    def delete(self, db: Session, id: int, id_field: str = 'id'):
        """
        删除记录
        :param db: 数据库会话
        :param id: 主键值
        :param id_field: 主键字段名，默认为'id'
        :return: 删除的对象
        """
        obj = db.exec(select(self.model).where(getattr(self.model, id_field) == id)).one()
        db.delete(obj)
        db.commit()
        return obj

    def _make_search(self, sql, search: BaseModel = None, filter_type: Optional[Dict[str, str]] = None):
        """
        用于构建专用的sql查询语句，子类需要重写此方法
        :param sql:
        :param search:
        :param filter_type:指定的各属性值判断形式
        :return:
        """
        if search is None:
            return sql
        if isinstance(search, BaseModel):
            q = deepcopy(search.model_dump())
        else:
            q = deepcopy(search)
        for key in q:
            if (key in filter_type.keys()) and (q[key] is not None and q[key] != '' and q[key] != []):
                if filter_type[key] == 'l_like':
                    sql = sql.where(
                        getattr(self.model, key).like(f'%{q[key]}'))
                elif filter_type[key] == 'r_like':
                    sql = sql.where(
                        getattr(self.model, key).like(f'{q[key]}%'))
                elif filter_type[key] == 'like':
                    sql = sql.where(
                        getattr(self.model, key).like(f'%{q[key]}%'))
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
                elif filter_type[key] == 'in':
                    sql = sql.where(getattr(self.model, key).in_(q[key]))
        return sql

    def _make_pagination(self, sql, subquery, search: Pagination, order_col: str):
        """
        创建分页,sql为外层，subquery用于查找最近的id
        """
        if search.model == 'desc':
            subquery = subquery.order_by(desc(getattr(self.model, order_col)))
        else:
            subquery = subquery.order_by(getattr(self.model, order_col))
        subquery = subquery.offset(
            (search.page - 1) * search.page_size).limit(1).scalar_subquery()
        # sql查询从subquery找到的order_col开始，并limit限制数量
        if search.model == 'desc':
            sql = sql.where(getattr(self.model, order_col) <= subquery).order_by(
                desc(getattr(self.model, order_col))).limit(
                search.page_size)
        else:
            sql = sql.where(getattr(self.model, order_col) >=
                            subquery).limit(search.page_size)
        return sql, subquery

    def search(self, session: Session, search: Pagination, filter_type: Optional[Dict[str, str]] = None,
               columns: Optional[List] = None, order_col: Optional[str] = 'id'):
        """
        分页查询方法
        :param session:
        :param search: Pagination实例对象，包含各搜索参数
        :param filter_type: 指定的各属性值判断形式
        :param columns: 查询返回指定columns
        :param order_col: order排序列名，默认id，此col需要为自增id
        :return:
        """
        if columns is None:
            sql = select(self.model)
        else:
            sql = select(*columns)
        sql = self._make_search(sql, search.search, filter_type)
        logger.debug(sql)
        # subquery查询找到order_col的起始值
        subquery = select(getattr(self.model, order_col))
        logger.debug(subquery)
        subquery = self._make_search(subquery, search.search, filter_type)
        sql, subquery = self._make_pagination(sql, subquery, search, order_col)
        logger.debug(sql)
        results = session.exec(sql).all()
        return results

    def search_total(self, session: Session, q: BaseModel, filter_type: Optional[Dict[str, str]] = None):
        """
        每次进行分页查询的时候，都需要返回一个total值，表示对应搜索，现阶段数据库有多少内容，便于前端分页数
        :param session:
        :param q:
        :param filter_type: 字段过滤形式
        :return:
        """
        sql = select(func.count(self.model.id))
        sql = self._make_search(sql, q, filter_type)
        logger.debug(str(sql))
        try:
            result = session.exec(sql).one()
        except NoResultFound:
            result = 0
        return result


class CRUDCategory(CRUDBase[ModelType], Generic[ModelType]):
    """
    CRUD操作类，专门用于处理分类表的增删改查
    主要用于处理分类表的增删改查，继承自CRUDBase
    1. get_last_category: 查询已有顶级分类，找到最大编号
    2. get_last_subcategory: 查询已有子分类，找到最大编号
    3. get_category: 通过code获取对应的分类
    4. delete_category_with_children: 删除分类及其子分类
    5. get_category_with_children: 获取分类及其子分类
    """

    def get_by_name(self, db: Session, name: str) -> Optional[ModelType]:
        """
        通过名称查询分类
        """
        sql = select(self.model).where(self.model.name == name)
        return db.exec(sql).first()

    def get_last_category(self, db: Session) -> Optional[ModelType]:
        """
        查询已有顶级分类，找到最大编号
        """
        sql = select(self.model).where(self.model.parent_id ==
                                       0).order_by(desc(self.model.code))
        return db.exec(sql).first()

    def get_last_subcategory(self, db: Session, parent_id: int) -> Optional[str]:
        # 获取当前父级分类下的最大子分类编号
        sql = select(self.model).where(self.model.parent_id ==
                                       parent_id).order_by(desc(self.model.code))
        return db.exec(sql).first()

    def get_category(self, db: Session, code: str | None = None) -> ModelType:
        """
        通过code获取对应的分类
        """
        sql = select(self.model)
        if code:
            sql = sql.where(self.model.code == code)
        return db.exec(sql).one()

    def delete_category_with_children(self, db: Session, code: str):
        """
        删除分类及其子分类
        """
        # 删除当前分类
        sql = delete(self.model).where(self.model.code.like(f"{code}%"))
        db.exec(sql)
        db.commit()

    def get_category_with_children(self, db: Session, code: str) -> ModelType:
        """
        获取分类及其子分类
        """
        sql = select(self.model)
        if code:
            sql = sql.where(self.model.code.like(f"{code}%"))
        return db.exec(sql).all()
