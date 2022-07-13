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


api = CRUDAPI(Api)
