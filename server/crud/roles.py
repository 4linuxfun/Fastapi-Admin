from typing import List, Optional
from sqlmodel import select, Session
from ..models import Role, Menu, RoleMenu, Category
from .base import CRUDBase
from ..dependencies import casbin_enforcer


class CRUDRole(CRUDBase[Role]):
    def get_roles_by_name(self, session: Session, roles: List[str]):
        return session.exec(select(self.model).where(self.model.name.in_(roles))).all()

    def check_admin(self, session: Session, uid: int) -> bool:
        """
        通过uid，判断此用户是否在admin组中
        :param session:
        :param uid:
        :return:
        """
        admin = session.exec(select(self.model).where(self.model.name == 'admin')).one()
        admin_users = [user.id for user in admin.users]
        if uid in admin_users:
            return True
        else:
            return False

    def get_all_menus(self, session: Session):
        return session.exec(select(Menu).where(Menu.enable == 1)).all()

    def get_roles_by_id(self, session: Session, id: int) -> List[id]:
        if id is not None:
            sql = select(RoleMenu).where(RoleMenu.role_id == id)
            result = session.exec(sql)
            role_menus = [role.menu_id for role in result]
        else:
            role_menus = []
        return role_menus

    def search(self, session: Session, q: Optional[str] = None) -> List[Role]:
        sql = select(self.model)
        if q is not None:
            sql = sql.where(self.model.name.like(f'%{q}%'))
        return session.exec(sql).all()

    def update_menus(self, session: Session, db_obj: Role, menus: List[int]):
        """
        更新角色信息，还涉及到角色关联的menus
        :param session:
        :param db_obj:
        :param menus:
        :return:
        """
        print(db_obj.menus)
        db_menus = session.exec(select(Menu).where(Menu.id.in_(menus))).all()
        db_obj.menus = db_menus
        casbin_enforcer.delete_permissions_for_user(f'role_{db_obj.id}')
        print(db_menus)
        for menu in db_menus:
            if (menu.api is None) or (len(menu.api.split(',')) == 0):
                continue
            for api in menu.api.split(','):
                method, path = api.split(':')
                print(f'增加权限:role_{db_obj.id},{path},{method}')
                casbin_enforcer.add_permission_for_user(f'role_{db_obj.id}', path, method, 'allow')
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)

    def update_categories(self, session: Session, db_obj: Role, categories: List[int]):
        category = session.exec(select(Category).where(Category.id.in_(categories))).all()
        db_obj.category = category
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)


role = CRUDRole(Role)
