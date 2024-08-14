from typing import Union
from loguru import logger
from sqlmodel import select, Session
from ...models.internal.playbook import Playbook
from ..base import CRUDBase
from ...models.internal.user import UserInfo, UserLogin
from .roles import role


class CRUDPlaybook(CRUDBase[Playbook]):

    def query_playbooks(self, session: Session, query: Union[str, None] = None):
        """
        通过名称查询playbook
        """
        sql = select(Playbook)
        if query:
            sql = sql.where(Playbook.name.like(f'%{query}%'))
        return session.exec(sql).all()


playbook = CRUDPlaybook(Playbook)
