""" 
资产分类管理路由模块

提供资产分类的CRUD操作接口，包括：
- 获取分类树形结构
- 新增分类
- 更新分类信息  
- 删除分类（带关联检查）

Author: Jing Wang
"""

from typing import Optional, List
from loguru import logger
from sqlmodel import Session
from fastapi import APIRouter, Depends

from app.common.response_code import ApiResponse
from app.common.database import get_session
from app.common.utils import Tree, generate_category_code
from app.common.auth_casbin import Authority
from app.models.assets import AssetsCategory, AssetsCategoryWithChild
from app import crud

router = APIRouter()


@router.get("/category/tree", summary="获取资产分类", dependencies=[Depends(Authority("assets:read"))],  response_model=ApiResponse[List[AssetsCategoryWithChild]])
async def get_category(name: str | None = None, code: str | None = None, session: Session = Depends(get_session)):
    """
    获取资产分类树形结构列表

    Args:
        name (str | None): 分类名称过滤条件，可选参数
        code (str | None): 分类编码过滤条件，可选参数
        session (Session): 数据库会话对象，通过依赖注入获取

    Returns:
        ApiResponse[List[AssetsCategoryWithChild]]: 包含分类树形结构的响应对象

    Note:
        - 返回完整的分类层级结构，包含父子关系
        - 需要 assets:read 权限
    """
    categories = crud.assets_category.get_all(session)
    logger.debug(f"get all category: {categories}")
    category_tree = Tree[AssetsCategoryWithChild](
        categories, AssetsCategoryWithChild).build()
    logger.debug(f"get category tree: {category_tree}")
    return ApiResponse(data=category_tree)


@router.post("/category", summary="新增分类", dependencies=[Depends(Authority("assetsCategory:add"))], response_model=ApiResponse)
async def create_category(category: AssetsCategory, session: Session = Depends(get_session)):
    """
    新增资产分类

    Args:
        category (AssetsCategory): 分类信息对象，包含分类名称、父级ID等
        session (Session): 数据库会话对象，通过依赖注入获取

    Returns:
        ApiResponse: 操作结果响应对象

    Note:
        - 如果parent_id为None，会自动设置为0（根分类）
        - 系统会自动生成分类编码
        - 需要 assetsCategory:add 权限

    Raises:
        Exception: 当数据库操作失败时抛出异常
    """

    logger.info(f"create category: {category}")
    if category.parent_id is None:
        category.parent_id = 0
    category.code = generate_category_code(
        category.parent_id, session, crud.assets_category)
    logger.debug(f"create category code: {category.code}")
    try:
        crud.assets_category.insert(session, category)
    except Exception as e:
        logger.error(f"create category error: {e}")
        return ApiResponse(code=500, message=str(e))
    return ApiResponse()


@router.put("/category", summary="更新分类", dependencies=[Depends(Authority("assetsCategory:update"))], response_model=ApiResponse)
async def update_category(category: AssetsCategory, session: Session = Depends(get_session)):
    """
    更新资产分类信息

    Args:
        category (AssetsCategory): 包含更新信息的分类对象，必须包含id字段
        session (Session): 数据库会话对象，通过依赖注入获取

    Returns:
        ApiResponse: 操作结果响应对象

    Note:
        - 根据category.id查找现有分类并更新
        - 需要 assetsCategory:update 权限

    Raises:
        Exception: 当数据库操作失败时抛出异常
    """
    logger.info(f"update category: {category}")
    try:
        crud.assets_category.update(
            session, crud.assets_category.get(session, category.id), category)
    except Exception as e:
        logger.error(f"update category error: {e}")
        return ApiResponse(code=500, message=str(e))
    return ApiResponse()


@router.delete("/category/{id}", summary="删除资产分类", dependencies=[Depends(Authority("assetsCategory:delete"))], response_model=ApiResponse)
async def logical_delete_category(id: int, session: Session = Depends(get_session)):
    """
    删除资产分类（物理删除）

    Args:
        id (int): 要删除的分类ID
        session (Session): 数据库会话对象，通过依赖注入获取

    Returns:
        ApiResponse: 操作结果响应对象
        - code=500: 删除失败（存在关联资产或子分类）
        - code=200: 删除成功

    Note:
        - 删除前会检查是否存在关联的资产信息
        - 删除前会检查是否存在子分类
        - 只有在没有关联数据时才能删除
        - 需要 assetsCategory:delete 权限

    Raises:
        Exception: 当数据库操作失败时抛出异常
    """
    try:
        asset_category = crud.assets_category.get(session, id)
        logger.debug(f"delete category: {asset_category}")
        if asset_category.assets:
            return ApiResponse(code=500, message="存在关联资产信息，无法删除")
        if len(crud.assets_category.get_category_with_children(
                session, asset_category.code)) > 1:
            return ApiResponse(code=500, message="存在子分类，无法删除")
        crud.assets_category.delete(session, id)
    except Exception as e:
        logger.error(f"delete category error: {e}")
        return ApiResponse(code=500, message=str(e))
    return ApiResponse()
