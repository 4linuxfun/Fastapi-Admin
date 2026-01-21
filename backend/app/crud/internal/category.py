from typing import Optional, List, Dict
from loguru import logger
from sqlmodel import select, Session, desc, delete
from ...models.internal.category import Category
from ..base import CRUDBase
from ...models.internal import Pagination


class CRUDCategory(CRUDBase[Category]):
    def get_last_category(self, db: Session) -> Optional[Category]:
        """
        查询已有顶级分类，找到最大编号
        """
        sql = select(self.model).where(self.model.parent_id ==
                                       0).order_by(desc(self.model.code))
        return db.exec(sql).first()

    def get_last_subcategory(self, db: Session, parent_id: int) -> Optional[str]:
        # 获取当前父级分类下的最大子分类编号
        sql = select(self.model).where(self.model.parent_id ==
                                       parent_id).order_by(desc(self.model.code))
        return db.exec(sql).first()

    def get_category(self, db: Session, code: str | None = None) -> Category:
        """
        通过code获取对应的分类
        """
        sql = select(self.model)
        if code:
            sql = sql.where(self.model.code == code)
        return db.exec(sql).one()

    def delete_category_with_children(self, db: Session, code: str):
        """
        删除分类及其子分类
        """
        # 删除当前分类
        sql = delete(self.model).where(self.model.code.like(f"{code}%"))
        db.exec(sql)
        db.commit()


category = CRUDCategory(Category)
