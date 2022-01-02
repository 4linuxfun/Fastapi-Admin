from typing import Union
from sqlmodel import select, Session, or_
from ..sql.models import User, Role
from .base import CRUDBase
from ..schemas.user import UserInfo, UserLogin
from .roles import role


class CRUDUser(CRUDBase):
    def login(self, session: Session, login_form: UserLogin) -> User:
        sql = select(self.model).where(self.model.name == login_form.username,
                                       self.model.password == login_form.password,
                                       self.model.enable == 1)
        return session.exec(sql).one()

    def search(self, session: Session, q: Union[int, str]):
        sql = select(User)
        if q is not None:
            sql = sql.where(or_(self.model.name.like(f'%{q}%'), ))
        return session.exec(sql).all()

    def insert(self, session: Session, user_info: UserInfo) -> User:
        updated_user = User(name=user_info.user.name, password=user_info.user.password, enable=user_info.user.enable)
        user_roles = role.get_roles_by_name(session, user_info.roles)
        updated_user.roles = user_roles
        return super(CRUDUser, self).insert(session, updated_user)

    def update(self, session: Session, uid: int, user_info: UserInfo):
        db_obj = self.get(session, uid)
        updated_user = user_info.user
        db_obj = super(CRUDUser, self).update(session, db_obj, updated_user)
        user_roles = role.get_roles_by_name(session, user_info.roles)
        db_obj.roles = user_roles
        print('update:')
        print(db_obj)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj


user = CRUDUser(User)
