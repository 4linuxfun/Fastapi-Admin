from typing import List, Union
from sqlmodel import select, Session, or_
from ...models.internal import Api
from ..base import CRUDBase


class CRUDAPI(CRUDBase[Api]):
    def get_multi(self, db: Session, id: List[int]) -> List[Api]:
        return db.exec(select(self.model).where(self.model.id.in_(id))).all()

    def get_tree(self, db: Session):
        tags = db.exec(select(self.model.tags).distinct(self.model.tags)).all()
        print(tags)
        tree_apis = []
        for tag in tags:
            child_apis = db.exec(select(self.model.id, self.model.summary).where(self.model.tags == tag)).all()
            tree_apis.append({'label': tag, 'options': child_apis})
        return tree_apis

    # 重写父类的查询构建命令
    def _make_search(self, sql, q: Union[int, str]):
        if q is not None:
            sql = sql.where(
                or_(self.model.tags.like(f'%{q}%'), self.model.path.like(f'%{q}%'),
                    self.model.method.like(f'%{q}%'),
                    self.model.summary.like(f'%{q}%')))
        return sql


api = CRUDAPI(Api)
