from typing import List
from loguru import logger
from sqlmodel import Session
from fastapi import APIRouter, Depends, status

from app.common.utils import Tree, generate_category_code
from app.common.response_code import ApiResponse
from app.common.database import get_session
from app.common.auth_casbin import Authority
from app.models.assets import AssetsLocation, AssetsLocationWithChild
from app import crud

router = APIRouter()


@router.get("/location/tree", summary="获取资产位置", dependencies=[Depends(Authority("assets:read"))], response_model=ApiResponse[List[AssetsLocationWithChild]])
async def get_location(session: Session = Depends(get_session)):
    """
    获取资产位置
    """
    locations = crud.assets_location.get_all(session)
    logger.debug(f"get all location: {locations}")
    location_tree = Tree[AssetsLocationWithChild](
        locations, AssetsLocationWithChild).build()
    return ApiResponse(data=location_tree)


@router.post("/location", summary="新增资产位置", dependencies=[Depends(Authority("assetsLocation:add"))], response_model=ApiResponse)
async def create_location(location: AssetsLocation, session: Session = Depends(get_session)):
    """
    新增资产位置
    """
    logger.info(f"create location: {AssetsLocation}")
    if location.parent_id is None:
        location.parent_id = 0
    location.code = generate_category_code(
        location.parent_id, session, crud.assets_location)
    logger.debug(f"create location code: {location.code}")
    try:
        crud.assets_location.insert(session, location)
    except Exception as e:
        logger.error(f"create location error: {e}")
        return ApiResponse(code=500, message=str(e))
    return ApiResponse()


@router.put("/location", summary="更新位置", dependencies=[Depends(Authority("assetsLocation:update"))], response_model=ApiResponse)
async def update_location(location: AssetsLocation, session: Session = Depends(get_session)):
    """
    更新位置名称
    """
    logger.info(f"update location: {location}")
    try:
        crud.assets_location.update(
            session, crud.assets_location.get(session, location.id), location)
    except Exception as e:
        logger.error(f"update location error: {e}")
        return ApiResponse(code=500, message=str(e))
    return ApiResponse()


@router.delete("/location/{id}", summary="删除位置", dependencies=[Depends(Authority("assetsLocation:delete"))], response_model=ApiResponse)
async def delete_location(id: int, session: Session = Depends(get_session)):
    """
    物理删除资产位置，但是会通过外键关联先检查是否存在关联资产信息，如果存在关联资产信息，则无法删除
    """
    try:
        asset_location = crud.assets_location.get(session, id)
        logger.debug(f"delete category: {asset_location}")
        if asset_location.assets:
            return ApiResponse(code=500, message="存在关联资产信息，无法删除")
        if len(crud.assets_location.get_category_with_children(
                session, asset_location.code)) > 1:
            return ApiResponse(code=500, message="存在子级位置，无法删除")
        crud.assets_location.delete(session, id)
    except Exception as e:
        logger.error(f"delete category error: {e}")
        return ApiResponse(code=500, message=str(e))
    return ApiResponse()
