from fastapi import APIRouter, Depends
from sqlmodel import Session, select, update, delete
from loguru import logger
from typing import List
from ...common.response_code import ApiResponse, SearchResponse
from ...common.auth_casbin import Authority
from ...common.database import get_session
from ...common.utils import generate_category_code
from ...models.internal.category import Category, CategoryWithChild
from ...models.internal import Pagination
from ... import crud

router = APIRouter(prefix="/api")


@router.get("/category/tree", summary="获取分类列表树形结构", response_model=ApiResponse[List[CategoryWithChild]])
async def get_category(name: str | None = None, code: str | None = None, session: Session = Depends(get_session)):
    """
    获取分类列表
    """
    def build_tree(categories, parent_id=0):
        tree = []
        for category in categories:
            logger.debug(f"category: {category}")
            if category.parent_id == parent_id:
                node = {
                    "id": category.id,
                    "name": category.name,
                    "code": category.code,
                    "children": build_tree(categories, category.id)
                }
                tree.append(node)
        logger.debug(f"get category tree: {tree}")
        return tree
    search = {'is_deleted': False}
    filter = {'is_deleted': 'eq'}
    parent_id = 0
    if code:
        # 传递code为分类查找
        search['code'] = code + '_'  # 模糊查询
        filter['code'] = 'r_like'
        parent_id = crud.internal.category.get_category(session, code).id
    categories = crud.internal.category.get_by_colume(
        session, search, filter)
    logger.debug(f"get category: {categories}")
    return ApiResponse(data=build_tree(categories, parent_id))


@router.post("/category", summary="新增分类", response_model=ApiResponse)
async def create_category(category: Category, session: Session = Depends(get_session)):
    """
    新增分类
    """
    logger.info(f"create category: {category}")
    if category.parent_id is None:
        category.parent_id = 0
    category.code = generate_category_code(category.parent_id, session)
    logger.debug(f"create category code: {category.code}")
    try:
        crud.internal.category.insert(session, category)
    except Exception as e:
        logger.error(f"create category error: {e}")
        raise ApiResponse(code=500, message=str(e))
    return ApiResponse()


@router.put("/category", summary="更新分类", response_model=ApiResponse)
async def update_category(category: Category, session: Session = Depends(get_session)):
    """
    更新分类名称
    """
    logger.info(f"update category: {category}")
    try:
        crud.internal.category.update(
            session, crud.internal.category.get(session, category.id), category)
    except Exception as e:
        logger.error(f"update category error: {e}")
        raise ApiResponse(code=500, message=str(e))
    return ApiResponse()


@router.delete("/category/logical/{id}", summary="逻辑删除分类", response_model=ApiResponse)
async def logical_delete_category(id: int, session: Session = Depends(get_session)):
    """
    逻辑删除分类，会同步删除子分类，is_deleted=True
    """
    try:
        category = crud.internal.category.get(session, id)
        logger.debug(f"delete category: {category}")
        sql = update(Category).where(Category.code.like(
            f"{category.code}%")).values(is_deleted=True)
        session.exec(sql)
        session.commit()
    except Exception as e:
        logger.error(f"delete category error: {e}")
        raise ApiResponse(code=500, message=str(e))
    return ApiResponse()
