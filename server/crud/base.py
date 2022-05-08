# 参考自：tiangolo/full-stack-fastapi-postgresql项目，部分代码为直接摘抄
from typing import TypeVar, Generic, List, Type, Union, Optional
from sqlmodel import Session, select, SQLModel, desc, func

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

    def _make_search(self, sql, q: Union[int, str]):
        """
        用于构建专用的sql查询语句，子类需要重写此方法
        :param sql:
        :param q:
        :return:
        """
        return sql

    def search(self, session: Session, q: Union[int, str], direction: str = 'next', id: Optional[int] = None,
               limit: Optional[int] = None, offset_page: Optional[int] = None):
        """
        分页查询方法，返回limit限制数量的数据，并通过direction指令，确定是上一页、下一页、当前页数据
        :param session:
        :param q:
        :param direction: next：下一页，prev：上一页，current：当前页，prev_page:向前多少页，next_page：向后多少页
        :param id:
        :param limit:
        :param offset_page:当direction为prev_page或next_page时，表示页面偏移多少页
        :return:
        """
        sql = select(self.model)
        print('sql')
        sql = self._make_search(sql, q)
        if direction == 'prev':
            sql = sql.where(self.model.id < id)
            sql = sql.order_by(desc(self.model.id)).limit(limit)
        elif direction == 'next':
            sql = sql.where(self.model.id > id)
            sql = sql.order_by(self.model.id).limit(limit)
        elif direction == 'current':
            sql = sql.where(self.model.id >= id)
            sql = sql.order_by(self.model.id).limit(limit)
        elif direction == 'prev_page':
            subquery = select(self.model.id).where(self.model.id < id).order_by(desc(self.model.id)).offset(
                offset_page * limit).limit(1).subquery()
            sql = sql.where(self.model.id >= subquery).order_by(self.model.id).limit(limit)
            print(sql)
        elif direction == 'next_page':
            subquery = select(self.model.id).where(self.model.id > id).order_by(self.model.id).offset(
                (offset_page - 1) * limit).limit(1).subquery()
            sql = sql.where(self.model.id >= subquery).order_by(self.model.id).limit(limit)
            print(sql)
        results = session.exec(sql).all()
        if direction == 'prev':
            results = results[::-1]
        return results

    def search_total(self, session: Session, q: Union[int, str]):
        """
        每次进行分页查询的时候，都需要返回一个total值，表示对应搜索，现阶段数据库有多少内容，便于前端分页数
        :param session:
        :param q:
        :return:
        """
        sql = select(func.count(self.model.id))
        sql = self._make_search(sql, q)
        print(sql)
        return session.execute(sql).scalar()
