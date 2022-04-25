from typing import List, Optional, Union
from sqlmodel import select, Session, or_
from ..models import Api
from .base import CRUDBase
from ..dependencies import casbin_enforcer


class CRUDAPI(CRUDBase[Api]):
    # 重写父类的查询构建命令
    def _make_search(self, sql, q: Union[int, str]):
        if q is not None:
            sql = sql.where(
                or_(self.model.tags.like(f'%{q}%'), self.model.path.like(f'%{q}%'), self.model.method.like(f'%{q}%'),
                    self.model.summary.like(f'%{q}%')))
        return sql


api = CRUDAPI(Api)
