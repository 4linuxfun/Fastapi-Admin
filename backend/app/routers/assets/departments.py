""" 
资产部门管理路由模块

提供资产部门的CRUD操作接口，包括：
- 获取部门树形结构
- 新增部门
- 更新部门信息  
- 删除部门（带关联检查）

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
from app.models.assets import AssetsDepartment, AssetsDepartmentWithChild
from app import crud

router = APIRouter()


@router.get("/department/tree", summary="获取资产部门", dependencies=[Depends(Authority("assets:read"))],  response_model=ApiResponse[List[AssetsDepartmentWithChild]])
async def get_department(name: str | None = None, code: str | None = None, session: Session = Depends(get_session)):
    """
    获取资产部门树形结构列表

    Args:
        name (str | None): 部门名称过滤条件，可选参数
        code (str | None): 部门编码过滤条件，可选参数
        session (Session): 数据库会话对象，通过依赖注入获取

    Returns:
        ApiResponse[List[AssetsDepartmentWithChild]]: 包含部门树形结构的响应对象

    Note:
        - 返回完整的部门层级结构，包含父子关系
        - 需要 assets:read 权限
    """
    departments = crud.assets_department.get_all(session)
    logger.debug(f"get all department: {departments}")
    department_tree = Tree[AssetsDepartmentWithChild](
        departments, AssetsDepartmentWithChild).build()
    logger.debug(f"get department tree: {department_tree}")
    return ApiResponse(data=department_tree)


@router.post("/department", summary="新增部门", dependencies=[Depends(Authority("assetsDepartment:add"))], response_model=ApiResponse)
async def create_department(department: AssetsDepartment, session: Session = Depends(get_session)):
    """
    新增资产部门

    Args:
        department (AssetsDepartment): 部门信息对象
        session (Session): 数据库会话对象，通过依赖注入获取

    Returns:
        ApiResponse: 操作结果响应对象

    Note:
        - 自动生成部门编码
        - 需要 assetsDepartment:add 权限
        - 如果parent_id为空，则设置为0（根部门）
    """
    logger.info(f"create department: {department}")
    if department.parent_id is None:
        department.parent_id = 0
    department.code = generate_category_code(
        department.parent_id, session, crud.assets_department)
    logger.debug(f"create department code: {department.code}")
    try:
        crud.assets_department.insert(session, department)
    except Exception as e:
        logger.error(f"create department error: {e}")
        return ApiResponse(code=500, message=str(e))
    return ApiResponse()


@router.put("/department", summary="更新部门", dependencies=[Depends(Authority("assetsDepartment:update"))], response_model=ApiResponse)
async def update_department(department: AssetsDepartment, session: Session = Depends(get_session)):
    """
    更新资产部门信息

    Args:
        department (AssetsDepartment): 更新的部门信息对象
        session (Session): 数据库会话对象，通过依赖注入获取

    Returns:
        ApiResponse: 操作结果响应对象

    Note:
        - 需要 assetsDepartment:update 权限
        - 只能更新部门名称，不能更改编码和父级关系
    """
    logger.info(f"update department: {department}")
    try:
        existing_department = crud.assets_department.get(session, department.id)
        if not existing_department:
            return ApiResponse(code=404, message="部门不存在")
        
        existing_department.name = department.name
        crud.assets_department.update(session, existing_department)
        return ApiResponse(message="部门更新成功")
    except Exception as e:
        logger.error(f"update department error: {e}")
        return ApiResponse(code=500, message=str(e))


@router.delete("/department/{id}", summary="删除资产部门", dependencies=[Depends(Authority("assetsDepartment:delete"))], response_model=ApiResponse)
async def logical_delete_department(id: int, session: Session = Depends(get_session)):
    """
    删除资产部门（逻辑删除）

    Args:
        id (int): 部门ID
        session (Session): 数据库会话对象，通过依赖注入获取

    Returns:
        ApiResponse: 操作结果响应对象

    Note:
        - 需要 assetsDepartment:delete 权限
        - 删除前会检查是否有关联的资产
        - 如果有关联资产，则不允许删除
        - 会同时删除所有子部门
    """
    logger.info(f"delete department id: {id}")
    try:
        # 检查是否有关联的资产
        asset_department = crud.assets_department.get(session, id)
        if asset_department.assets:
            return ApiResponse(code=400, message=f"该部门下还有 {len(asset_department.assets)} 个资产，无法删除")
        
        # 检查是否有子部门
        child_departments = crud.assets_department.get_children(session, id)
        if child_departments:
            return ApiResponse(code=400, message="该部门下还有子部门，请先删除子部门")
        
        # 执行删除
        result = crud.assets_department.delete(session, id)
        if result:
            return ApiResponse(message="部门删除成功")
        else:
            return ApiResponse(code=404, message="部门不存在")
    except Exception as e:
        logger.error(f"delete department error: {e}")
        return ApiResponse(code=500, message=str(e))