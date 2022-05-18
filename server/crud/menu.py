from typing import Optional, List
from sqlmodel import Session, select
from ..models.menu import Menu
from .base import CRUDBase
from .sysapi import api
from ..dependencies import casbin_enforcer


class CRUDMenu(CRUDBase[Menu]):
    def search(self, session: Session, q: Optional = None) -> List[Menu]:
        sql = select(self.model)
        if q is not None:
            sql = sql.where(self.model.name.like(f'%{q}%'))
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

    def delete(self, session: Session, *, id: int):
        db_obj = self.get(session, id)
        if db_obj.api is not None:
            apis: List[str] = db_obj.api.split(',')
            roles: List[int] = [role.id for role in db_obj.roles]
            if apis and roles:
                for api in apis:
                    method, path = api.split(':')
                    for role in roles:
                        casbin_enforcer.delete_permission_for_user(f'role_{role}', path, method, 'allow')
        session.delete(db_obj)
        session.commit()


menu = CRUDMenu(Menu)
