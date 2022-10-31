from typing import Optional, List
from sqlmodel import Session, select
from ...models.internal.menu import Menu
from ..base import CRUDBase


class CRUDMenu(CRUDBase[Menu]):
    def search(self, session: Session, q: Optional = None) -> List[Menu]:
        sql = select(self.model)
        if q is not None:
            sql = sql.where(self.model.name.like(f'%{q}%'))
        sql = sql.order_by(self.model.sort)
        return session.exec(sql).all()

    def update(self, session: Session, db_obj, obj_in: Menu):
        """
        菜单的更新，1. 更新基础内容，2. 更新apis.
        roles的更新，应该在角色管理里，菜单里不涉及关联角色的更新
        :param session:
        :param db_obj:
        :param obj_in:
        :return:
        """
        print(db_obj)
        return super(CRUDMenu, self).update(session, db_obj, obj_in)

    def delete(self, session: Session, id: int):
        db_obj = self.get(session, id)
        session.delete(db_obj)
        session.commit()


menu = CRUDMenu(Menu)
