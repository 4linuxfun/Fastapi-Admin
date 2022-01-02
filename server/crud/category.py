from typing import List, Optional
from sqlmodel import select, Session, or_
from ..sql.models import Category, RoleCategory, CategoryField
from .base import CRUDBase


class CRUECategory(CRUDBase):
    def get_all_catagories(self, session: Session) -> List[Category]:
        return session.exec(select(Category)).all()

    def get_categories_by_roles(self, session: Session, id: int) -> List[int]:
        if id is not None:
            sql = select(RoleCategory).where(RoleCategory.role_id == id)
            result = session.exec(sql)
            role_category = [role.category_id for role in result]
        else:
            role_category = []
        return role_category

    def get_category_fields(self, session: Session, id: int) -> List[CategoryField]:
        return session.exec(select(CategoryField).where(CategoryField.category_id == id)).all()

    def get_role_categories(self, session: Session, id: List[int], search: Optional[str] = None) -> List[Category]:
        sql = select(self.model).where(self.model.id.in_(id))
        if search is not None:
            sql = sql.where(self.model.name.like('%' + search + '%'))
        return session.exec(sql).all()

    def update_fields(self, session: Session, db_obj: Category, fields):
        db_obj.fields = fields
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj


category = CRUECategory(Category)
