from typing import Optional, List
from sqlmodel import Session, select
from ..sql.models import Menu
from .base import CRUDBase
from ..dependencies import casbin_enforcer


class CRUDMenu(CRUDBase[Menu]):
    def search(self, session: Session, q: Optional = None) -> List[Menu]:
        sql = select(self.model)
        if q is not None:
            sql = sql.where(self.model.name.like(f'%{q}%'))
        return session.exec(sql).all()

    def update(self, session: Session, db_obj, obj_in: Menu):
        original_roles = [role.id for role in db_obj.roles]
        print(db_obj)
        # 权限更新原则：统一删除原来的，然后统一增加新的

        for role in original_roles:
            print('删除')
            casbin_enforcer.delete_permissions_for_user(f'role_{role}')
        for api in obj_in.api.split(','):
            method, path = api.split(':')
            for role in original_roles:
                print(f'更新:role_{role},{path},{method}')
                casbin_enforcer.add_permission_for_user(f'role_{role}', path, method, 'allow')
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
