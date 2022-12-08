from typing import List, Optional
from loguru import logger
from sqlmodel import select, Session
from ...models.internal import Role, Menu, RoleMenu
from ..base import CRUDBase
from ...settings import casbin_enforcer


class CRUDRole(CRUDBase[Role]):
    def get_roles_by_id(self, session: Session, roles: List[str]):
        return session.exec(select(self.model).where(self.model.id.in_(roles))).all()

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

    def get_enable_menus(self, session: Session, id: int) -> List[id]:
        if id is not None:
            sql = select(self.model).where(self.model.id == id)
            role: Role = session.exec(sql).one()
            role_menus = [menu.id for menu in role.menus]
        else:
            role_menus = []
        return role_menus

    def update_menus(self, session: Session, db_obj: Role, menus: List[int]):
        """
        更新角色信息，还涉及到角色关联的menus
        :param session:
        :param db_obj:
        :param menus:
        :return:
        """
        logger.debug(db_obj.menus)
        db_menus = session.exec(select(Menu).where(Menu.id.in_(menus))).all()
        db_obj.menus = db_menus
        casbin_enforcer.delete_permissions_for_user(f'role_{db_obj.id}')
        logger.debug(db_menus)
        for menu in db_menus:
            if (menu.auth is not None) and menu.auth:
                model, act = menu.auth.split(':')
                logger.debug(f'增加权限:role_{db_obj.id},{model},{act}')
                casbin_enforcer.add_permission_for_user(f'role_{db_obj.id}', model, act)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)


role = CRUDRole(Role)
