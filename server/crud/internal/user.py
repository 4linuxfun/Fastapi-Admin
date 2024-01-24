from typing import Union
from loguru import logger
from sqlmodel import select, Session
from ...models.internal.user import User
from ..base import CRUDBase
from ...models.internal.user import UserInfo, UserLogin
from .roles import role


class CRUDUser(CRUDBase[User]):
    def login(self, session: Session, login_form: UserLogin) -> User:
        sql = select(self.model).where(self.model.name == login_form.username,
                                       self.model.password == login_form.password,
                                       self.model.enable == 1)
        return session.exec(sql).one()

    def check_name(self, session: Session, name: str):
        sql = select(self.model).where(self.model.name == name)
        return session.exec(sql).one()

    def insert(self, session: Session, user_info: UserInfo) -> User:
        updated_user = User(**user_info.user.dict())
        user_roles = role.get_roles_by_id(session, user_info.roles)
        updated_user.roles = user_roles
        return super(CRUDUser, self).insert(session, updated_user)

    def update(self, session: Session, uid: int, user_info: UserInfo):
        db_obj = self.get(session, uid)
        updated_user = user_info.user
        db_obj = super(CRUDUser, self).update(session, db_obj, updated_user)
        user_roles = role.get_roles_by_id(session, user_info.roles)
        db_obj.roles = user_roles
        logger.debug('update:')
        logger.debug(db_obj)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update_passwd(self, session: Session, uid: int, passwd: str):
        db_obj = self.get(session, uid)
        db_obj.password = passwd
        session.add(db_obj)
        session.commit()


user = CRUDUser(User)
