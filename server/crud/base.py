# 参考自：tiangolo/full-stack-fastapi-postgresql项目，部分代码为直接摘抄
from typing import TypeVar, Generic, List, Type
from sqlmodel import Session, select, SQLModel

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

    def delete(self, db: Session, *, id: int):
        obj = db.exec(select(self.model).where(self.model.id == id))
        db.delete(obj)
        db.commit()
        return obj
