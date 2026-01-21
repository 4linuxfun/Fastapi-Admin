import json
import os
from io import BytesIO
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union, Tuple, Annotated
from loguru import logger
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
import pandas as pd
import numpy as np
from fastapi import APIRouter, Depends, Form, Request, UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse

from app.common.response_code import ApiResponse, SearchResponse
from app.common.database import get_session, get_session_with_transaction
from app.common.auth_casbin import Authority
from app.common.utils import upload_files
from app.models.internal import Pagination
from app.common.dep import get_uid
from app.models.assets import (
    Assets, AssetsSearch, AssetLogs, AssetsCategory, AssetsLocation, AssetsDepartment, AssetWithCategory, AssetsAllocation, AssetsReturn, AssetsDisposal, AssetsTransfer, AssetLogsSearch, AssetLogsWithAssetInfo
)
from app import crud
from app.settings import settings
# 导入通用路径构建函数
from app.common.utils import build_hierarchical_path


def create_asset_log(session: Session, asset_id: int, user_id: int, action: str, details: str):
    """
    创建资产操作日志
    :param session:
    :param asset_id:
    :param user_id:
    :param action:
    :param details:
    :return:
    """
    asset_log = AssetLogs(asset_id=asset_id, user_id=user_id,
                          action=action, details=details)
    session.add(asset_log)
    session.commit()
    session.refresh(asset_log)
    return asset_log


def build_hierarchical_path_mapping(all_entities: List, unique_paths: List[str], entity_type: str) -> Dict[str, int]:
    """
    构建层级路径到ID的映射
    
    Args:
        all_entities: 所有实体数据列表
        unique_paths: 唯一路径列表
        entity_type: 实体类型（用于日志）
    
    Returns:
        Dict[str, int]: 路径到ID的映射字典
    """
    id_mapping = {}
    
    # 添加调试信息，输出所有实体数据
    logger.debug(
        f"所有{entity_type}数据: {[(entity.id, entity.name, entity.parent_id) for entity in all_entities]}")

    # 处理每个路径
    for path in unique_paths:
        # 分割路径，如 "东东楼/二楼/MIS机房" -> ["东东楼", "二楼", "MIS机房"]
        path_parts = path.split('/')
        logger.debug(f"处理{entity_type}路径: {path}, 分割后: {path_parts}")

        # 构建完整路径到当前节点的映射
        current_path = ""
        current_id = None
        found = True

        for i, part in enumerate(path_parts):
            # 构建当前层级的完整路径
            if i == 0:
                current_path = part
            else:
                current_path = f"{current_path}/{part}"

            logger.debug(
                f"当前处理层级 {i}: {part}, 当前路径: {current_path}, 上级ID: {current_id}")

            # 在当前父节点下查找匹配的实体
            found_entity = None
            matched_entities = []

            for entity in all_entities:
                # 对于第一级，查找parent_id为0或None的节点
                if i == 0 and (entity.parent_id == 0 or entity.parent_id is None) and entity.name == part:
                    found_entity = entity
                    matched_entities.append(
                        (entity.id, entity.name, entity.parent_id))
                # 对于其他级别，查找parent_id为上一级ID的节点
                elif i > 0 and entity.parent_id == current_id and entity.name == part:
                    found_entity = entity
                    matched_entities.append(
                        (entity.id, entity.name, entity.parent_id))

            logger.debug(f"层级 {i} 匹配到的{entity_type}: {matched_entities}")

            if found_entity:
                current_id = found_entity.id
                logger.debug(
                    f"找到匹配{entity_type}: ID={found_entity.id}, 名称={found_entity.name}, 父ID={found_entity.parent_id}")
            else:
                found = False
                logger.debug(f"未找到匹配{entity_type}，路径匹配失败")
                break

        # 如果找到完整路径匹配，添加到映射
        if found and current_id is not None:
            id_mapping[path] = current_id
            logger.debug(f"完整{entity_type}路径匹配成功: {path} -> {current_id}")
        else:
            logger.debug(f"完整{entity_type}路径匹配失败: {path}")

    logger.debug(f"{entity_type}_id_mapping: {id_mapping}")
    return id_mapping


# 为了保持向后兼容，保留原函数名但使用通用实现
def build_location_full_path(session: Session, location_id: int) -> str:
    """
    构建位置的完整路径
    例如：东楼/二楼/MIS机房
    """
    return build_hierarchical_path(session, location_id, crud.assets_location)


router = APIRouter()


@router.post("/search", summary="查找资产", dependencies=[Depends(Authority("assets:read"))], response_model=ApiResponse[SearchResponse[AssetWithCategory]])
async def search(search: Pagination[AssetsSearch], session: Session = Depends(get_session)):
    logger.debug(f"search assets: {search}")
    filter = {"name": "like",
              "asset_code": "like",
              "serial_number": "like",
              "financial_code": 'like',
              "status": "eq",
              "model": "like",
              "brand": "like",
              "owner": 'like'}

    # 增加category_id过滤
    if search.search.category_code:
        categories: List[AssetsCategory] = crud.assets_category.get_category_with_children(
            session, search.search.category_code)
        category_ids = [category.id for category in categories]
        search.search.category_id = category_ids
        filter['category_id'] = 'in'
        logger.debug(f"search assets category: {categories}")
    del search.search.category_code

    # 增加location_id过滤
    if search.search.location_code:
        locations: List[AssetsLocation] = crud.assets_location.get_category_with_children(
            session, search.search.location_code)
        location_ids = [location.id for location in locations]
        search.search.location_id = location_ids
        filter['location_id'] = 'in'
        logger.debug(f"search assets location: {locations}")
    del search.search.location_code

    # 增加department_id过滤
    if search.search.department_code:
        departments: List[AssetsDepartment] = crud.assets_department.get_category_with_children(
            session, search.search.department_code)
        department_ids = [department.id for department in departments]
        search.search.department_id = department_ids
        filter['department_id'] = 'in'
        logger.debug(f"search assets department: {departments}")
    del search.search.department_code

    total = crud.assets.search_total(
        session, search.search, filter
    )
    logger.debug(f'search assets total:{total}')
    assets = crud.assets.search(
        session, search, filter, order_col='updated_at')
    logger.debug(f'search assets:{assets}')
    assets_with_category: List[AssetWithCategory] = []
    for asset, category, location, department in assets:
        # 构建完整的位置路径
        location_full_path = build_location_full_path(
            session, asset.location_id)
        # 构建完整的部门路径
        department_full_path = build_hierarchical_path(
            session, asset.department_id, crud.assets_department) if asset.department_id else ""

        asset_read = AssetWithCategory(
            **asset.model_dump(),
            category_name=category.name if category else None,
            location_name=location_full_path or (
                location.name if location else None),  # 使用完整路径，如果为空则使用位置名称
            department_name=department_full_path or (
                department.name if department else None)  # 使用完整路径，如果为空则使用部门名称
        )
        assets_with_category.append(asset_read)
    return ApiResponse(data={"total": total, "data": assets_with_category})


@router.get('/logs/{id}', summary="获取资产操作日志", dependencies=[Depends(Authority("assets:read"))], response_model=ApiResponse[List[AssetLogs]])
async def get_asset_logs(id: int, start: Union[date, None] = None, end: Union[date, None] = None, session: Session = Depends(get_session)):
    """
    获取资产操作日志
    :param search:
    :param session:
    :return:
    """
    logger.debug(f"get asset logs: {id}, {start}, {end}")
    logs = crud.assets_logs.get_asset_logs(session, id, start, end)
    logger.debug(f"get asset logs: {logs}")
    return ApiResponse(data=logs)


@router.get('/logs', summary="获取最近操作日志", dependencies=[Depends(Authority("assets:read"))], response_model=ApiResponse[List[AssetLogs]])
async def get_recent_logs(start: Union[datetime, None] = None, end: Union[datetime, None] = None, session: Session = Depends(get_session)):
    """
    获取资产操作日志
    :param search:
    :param session:
    :return:
    """
    logs = crud.assets_logs.get_recent_logs(session, start, end)
    return ApiResponse(data=logs)


@router.get('/logs/user/{username}', summary="获取用户资产操作日志", dependencies=[Depends(Authority("assets:read"))], response_model=ApiResponse[List[AssetLogs]])
async def get_user_logs(username: str, start: Union[date, None] = None, end: Union[date, None] = None, session: Session = Depends(get_session)):
    """
    获取指定用户的资产领用和退回日志
    :param username: 用户名
    :param start: 开始日期
    :param end: 结束日期
    :param session: 数据库会话
    :return: 用户的资产操作日志列表
    """
    logger.debug(f"get user logs: {username}, {start}, {end}")
    logs = crud.assets_logs.get_user_logs(session, username, start, end)
    logger.debug(f"get user logs result: {logs}")
    return ApiResponse(data=logs)


@router.post('/logs/search', summary="搜索资产操作日志", dependencies=[Depends(Authority("assets:read"))], response_model=ApiResponse[SearchResponse[AssetLogsWithAssetInfo]])
async def search_asset_logs(search: Pagination[AssetLogsSearch], session: Session = Depends(get_session)):
    """
    搜索资产操作日志，支持多种过滤条件和分页
    :param search: 搜索参数，包含分页信息和过滤条件
    :param session: 数据库会话
    :return: 分页的资产日志列表
    """
    try:
        # 定义过滤器类型，指定每个字段的搜索方式
        filter_type = {
            'asset_id': 'eq',           # 资产ID精确匹配
            'asset_code': 'like',       # 资产编号模糊匹配
            'asset_name': 'like',       # 资产名称模糊匹配
            'operator': 'like',         # 操作人模糊匹配
            'action': 'eq',             # 操作类型精确匹配
            'category_id': 'eq',        # 分类ID精确匹配
            'location_id': 'eq',        # 位置ID精确匹配
            'department_id': 'eq',      # 部门ID精确匹配
            'start_time': 'gte',        # 开始时间大于等于
            'end_time': 'lte'           # 结束时间小于等于
        }
        
        # 调用CRUD层进行搜索，将filter_type作为独立参数传递
        result = crud.assets_logs.search_logs(session, search, filter_type)
        return ApiResponse(data=result)
    except Exception as e:
        logger.error(f"Search Asset Logs Error: {str(e)}")
        return ApiResponse(code=500, message=str(e))





@router.get('/status', summary="获取资产总体信息", dependencies=[Depends(Authority("assets:read"))], response_model=ApiResponse[List[Tuple[str, int]]])
async def get_assets_status(session: Session = Depends(get_session)):
    """
    获取资产总体信息
    :param session:
    :return:
    """
    try:
        status_counts = crud.assets.get_status_counts(session)
        logger.debug(f"status counts: {status_counts}")
    except Exception as e:
        logger.error(f"获取资产各状态总数报错: {str(e)}")
        return ApiResponse(code=500, message=str(e))
    return ApiResponse(data=status_counts)

# 资产的所有生命过程都独立API接口，防止部分资产信息被篡改


@router.post('/entry', summary="资产录入", dependencies=[Depends(Authority("assets:add"))], response_model=ApiResponse[Assets])
async def entry_asset(request: Request,
                      name: Annotated[str, Form()],
                      category_id: Annotated[int, Form()],
                      location_id: Annotated[int, Form()],
                      serial_number: Annotated[str, Form()],
                      model: Annotated[str, Form()],
                      brand: Annotated[str, Form()],
                      purchase_date: Annotated[Union[date,
                                                     None], Form()] = None,
                      #   files: List[UploadFile],
                      financial_code: Annotated[Union[str,
                                                      None], Form()] = None,
                      specifications: Annotated[Union[str,
                                                      None], Form()] = None,
                      remarks: Annotated[Union[str, None], Form()] = None,
                      department_id: Annotated[Union[int,
                                                     None], Form()] = None,
                      session: Session = Depends(get_session_with_transaction), uid: int = Depends(get_uid)):
    """
    资产录入
    :param asset:
    :param session:
    :return:
    """
    try:
        current_time = datetime.now()
        # form-data uploadfile不固定name属性，通过request.form()获取form表单，for循环获取附件
        form_data = await request.form()
        files = []
        for key, value in form_data.multi_items():
            logger.debug(f"Key: {key}, Type: {type(value)}")
            if isinstance(value, StarletteUploadFile):
                files.append(value)
                logger.debug(f"Added file: {value.filename} to files list")
            else:
                logger.debug(f"Value is not UploadFile: {value}")
        logger.debug('upload files: %s', files)
        image_paths = await upload_files(files, settings.upload_dir)
        logger.debug(f"image paths: {image_paths}")
        asset = Assets(
            name=name,
            category_id=category_id,
            location_id=location_id,
            serial_number=serial_number,
            financial_code=financial_code,
            specifications=specifications,
            model=model,
            brand=brand,
            remarks=remarks,
            created_at=current_time,
            updated_at=current_time,
            purchase_date=purchase_date,
            department_id=department_id,
            image_urls=image_paths,
        )
        asset.asset_code = crud.assets.generate_asset_code(
            session, settings.asset_prefix)
        asset.status = '0'
        logger.debug(f"create asset: {asset}")
        asset = crud.assets.insert(session, asset)
        change_info = jsonable_encoder(asset)
        # 构建完整的位置和部门层级路径
        location_full_path = build_hierarchical_path(
            session, asset.location_id, crud.assets_location) if asset.location_id else ""
        department_full_path = build_hierarchical_path(
            session, asset.department_id, crud.assets_department) if asset.department_id else ""

        change_info['location'] = location_full_path or (
            asset.location.name if asset.location else "")
        change_info['category'] = asset.category.name
        if asset.department:
            change_info['department'] = department_full_path or asset.department.name
        operator = crud.internal.user.get(session, uid).name
        image_paths_str = json.dumps(image_paths) if image_paths else None
        crud.assets_logs.insert(
            session, AssetLogs(action="资产录入", asset_id=asset.id,
                               details=json.dumps(change_info),
                               operator=operator, images=image_paths_str, timestamp=datetime.now()))
    except Exception as e:
        logger.error(f"Asset Add Error:{str(e)}")
        return ApiResponse(
            code=500,
            message=str(e)
        )
    return ApiResponse()


@router.post('/update', summary="资产更新", dependencies=[Depends(Authority("assets:add"))], response_model=ApiResponse[Assets])
async def update_asset(request: Request,
                       id: Annotated[int, Form()],
                       #    files: Union[List[UploadFile], None] = None,
                       name: Annotated[Union[str,
                                             None], Form()] = None,
                       category_id: Annotated[Union[int,
                                                    None], Form()] = None,
                       location_id: Annotated[Union[int,
                                                    None], Form()] = None,
                       serial_number: Annotated[Union[str,
                                                      None], Form()] = None,
                       model: Annotated[Union[str,
                                              None], Form()] = None,
                       brand: Annotated[Union[str,
                                              None], Form()] = None,
                       purchase_date: Annotated[Union[date,
                                                      None], Form()] = None,
                       financial_code: Annotated[Union[str,
                                                       None], Form()] = None,
                       specifications: Annotated[Union[str,
                                                       None], Form()] = None,
                       remarks: Annotated[Union[str, None], Form()] = None,
                       department_id: Annotated[Union[int,
                                                      None], Form()] = None,
                       existing_images: Annotated[Union[List[str], None], Form(
                       )] = None,
                       session: Session = Depends(get_session_with_transaction), uid: int = Depends(get_uid)):
    """
    资产更新
    :param asset:
    :param session:
    :return:
    """
    try:
        current_time = datetime.now()
        form_data = await request.form()
        files = []
        for key, value in form_data.multi_items():
            logger.debug(f"Key: {key}, Type: {type(value)}")
            if isinstance(value, StarletteUploadFile):
                files.append(value)
                logger.debug(f"Added file: {value.filename} to files list")
            else:
                logger.debug(f"Value is not UploadFile: {value}")
        logger.debug('upload files: %s', files)
        new_image_paths = await upload_files(files, settings.upload_dir)

        # 合并现有图片和新上传的图片
        if existing_images:
            logger.debug(f"existing images: {existing_images}")
            image_paths = existing_images + new_image_paths
        else:
            image_paths = new_image_paths
        logger.debug(f"final image paths: {image_paths}")

        asset = Assets(
            id=id,
            name=name,
            category_id=category_id,
            location_id=location_id,
            serial_number=serial_number,
            financial_code=financial_code,
            specifications=specifications,
            model=model,
            brand=brand,
            purchase_date=purchase_date,
            remarks=remarks,
            updated_at=current_time,
            department_id=department_id,
            image_urls=image_paths,
        )
        logger.debug(f"update asset: {asset}")
        db_asset = crud.assets.get(session, asset.id)
        logger.debug(f"db asset: {db_asset}")
        if db_asset.status != '0':
            return ApiResponse(
                code=500,
                message="该资产不在库，无法修改"
            )
        new_asset = crud.assets.update(
            session, db_asset, asset)
        operator = crud.internal.user.get(session, uid).name
        change_info = jsonable_encoder(new_asset)
        # 构建完整的位置和部门层级路径
        location_full_path = build_hierarchical_path(
            session, new_asset.location_id, crud.assets_location) if new_asset.location_id else ""
        department_full_path = build_hierarchical_path(
            session, new_asset.department_id, crud.assets_department) if new_asset.department_id else ""

        change_info['location'] = location_full_path or (
            new_asset.location.name if new_asset.location else "")
        change_info['category'] = new_asset.category.name
        if new_asset.department:
            change_info['department'] = department_full_path or new_asset.department.name
        image_paths_str = json.dumps(
            image_paths) if image_paths else None
        crud.assets_logs.insert(
            session, AssetLogs(action="资产编辑", asset_id=asset.id, details=json.dumps(change_info), operator=operator, images=image_paths_str, timestamp=datetime.now()))
    except Exception as e:
        logger.error(f"Asset update Error:{str(e)}")
        raise e
    return ApiResponse()


@router.post('/allocation', summary="资产领用", dependencies=[Depends(Authority("assets:allocation"))], response_model=ApiResponse[Assets])
async def allocation_asset(request: Request,
                           id: Annotated[int, Form()],
                           location_id: Annotated[int, Form()],
                           owner: Annotated[str, Form()],
                           department_id: Annotated[Union[int, None], Form(
                           )] = None,
                           remarks: Annotated[Union[str, None], Form()] = None,
                           session: Session = Depends(get_session_with_transaction), uid: int = Depends(get_uid)):
    """
    资产领用
    :param asset:
    :param session:
    :return:
    """
    try:
        current_time = datetime.now()
        # form-data uploadfile不固定name属性，通过request.form()获取form表单，for循环获取附件
        form_data = await request.form()
        files = []
        for key, value in form_data.multi_items():
            logger.debug(f"Key: {key}, Type: {type(value)}")
            if isinstance(value, StarletteUploadFile):
                files.append(value)
                logger.debug(f"Added file: {value.filename} to files list")
            else:
                logger.debug(f"Value is not UploadFile: {value}")
        logger.debug('upload files: %s', files)
        image_paths = await upload_files(files, settings.upload_dir)
        logger.debug(f"image paths: {image_paths}")

        # 创建资产领用对象
        asset = AssetsAllocation(
            id=id,
            location_id=location_id,
            department_id=department_id,
            owner=owner,
            remarks=remarks,
            updated_at=current_time,
            status=1,
            image_urls=image_paths if image_paths else None
        )

        logger.debug(f"Asset Allocation: {asset}")
        db_asset = crud.assets.get(session, asset.id)
        logger.debug(f"db asset: {db_asset}")
        if db_asset.status != '0':
            return ApiResponse(
                code=500,
                message="该资产不在库，无法领用"
            )

        asset_info = crud.assets.update(
            session, db_asset, asset)
        # 构建完整的位置和部门层级路径
        location_full_path = build_hierarchical_path(
            session, asset_info.location_id, crud.assets_location) if asset_info.location_id else ""
        department_full_path = build_hierarchical_path(
            session, asset_info.department_id, crud.assets_department) if asset_info.department_id else ""

        change_info = {
            "owner": asset_info.owner,
            "location": location_full_path or (asset_info.location.name if asset_info.location else ""),
            "department": department_full_path or (asset_info.department.name if asset_info.department else ""),
            "remarks": asset_info.remarks,
            "updated_at": asset_info.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": asset_info.status,
            "asset_name": asset_info.name,
            "asset_code": asset_info.asset_code,
            "category": asset_info.category.name if asset_info.category else "",
            "model": asset_info.model,
            "brand": asset_info.brand,
            "serial_number": asset_info.serial_number
        }
        operator = crud.internal.user.get(session, uid).name
        image_paths_str = json.dumps(image_paths) if image_paths else None
        asset_log = AssetLogs(action="资产领用", asset_id=asset.id, details=json.dumps(
            change_info), operator=operator, images=image_paths_str, timestamp=datetime.now())
        crud.assets_logs.insert(session, asset_log)
    except Exception as e:
        logger.error(f"资产领用报错:{str(e)}")
        raise e
    return ApiResponse()


@router.post('/return', summary="资产退回", dependencies=[Depends(Authority("assets:return"))], response_model=ApiResponse[Assets])
async def return_asset(request: Request,
                       id: Annotated[int, Form()],
                       location_id: Annotated[int, Form()],
                       remarks: Annotated[Union[str, None], Form()] = None,
                       #    files: List[UploadFile],
                       session: Session = Depends(get_session_with_transaction), uid: int = Depends(get_uid)):
    """
    资产退回信息部
    :param asset:
    :param session:
    :return:
    """
    try:
        current_time = datetime.now()
        form_data = await request.form()
        files = []
        for key, value in form_data.multi_items():
            logger.debug(f"Key: {key}, Type: {type(value)}")
            if isinstance(value, StarletteUploadFile):
                files.append(value)
                logger.debug(f"Added file: {value.filename} to files list")
            else:
                logger.debug(f"Value is not UploadFile: {value}")
        logger.debug('upload files: %s', files)
        image_paths = await upload_files(files, settings.upload_dir)
        # 将图片路径集成到AssetsReturn对象中
        return_asset = AssetsReturn(
            id=id,
            location_id=location_id,
            status=0,
            owner=None,
            department_id=None,  # 退回时重置使用部门
            updated_at=current_time,
            image_urls=image_paths if image_paths else None
        )
        logger.debug(f"Asset Return: {return_asset}")
        db_asset = crud.assets.get(session, id)
        previous_owner = db_asset.owner
        previous_department_id = db_asset.department_id
        # 构建原有使用部门的完整层级路径
        previous_department_full_path = ""
        if previous_department_id:
            previous_department_full_path = build_hierarchical_path(
                session, previous_department_id, crud.assets_department)

        logger.debug(f"db asset: {db_asset}")
        if db_asset.status != '1':
            return ApiResponse(
                code=500,
                message="该资产未领用，无法退回"
            )

        new_asset = crud.assets.update(
            session, db_asset, return_asset)
        # 构建完整的位置层级路径
        location_full_path = build_hierarchical_path(
            session, new_asset.location_id, crud.assets_location) if new_asset.location_id else ""

        change_info = {
            "location": location_full_path or (new_asset.location.name if new_asset.location else ""),
            "previous_owner": previous_owner,  # 记录原领用人
            "previous_department_full_path": previous_department_full_path,  # 记录原使用部门完整路径
            "asset_name": new_asset.name,
            "asset_code": new_asset.asset_code,
            "category": new_asset.category.name if new_asset.category else "",
            "updated_at": new_asset.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "model": new_asset.model,
            "brand": new_asset.brand,
            "serial_number": new_asset.serial_number,
            "status": new_asset.status,
            "remarks": remarks or ""  # 添加备注信息
        }
        operator = crud.internal.user.get(session, uid).name
        image_paths_str = json.dumps(
            image_paths) if image_paths else None
        crud.assets_logs.insert(
            session, AssetLogs(action="资产退回", asset_id=new_asset.id, details=json.dumps(change_info),
                               operator=operator, images=image_paths_str, timestamp=datetime.now()))
    except Exception as e:
        logger.error(f"资产领用报错:{str(e)}")
        raise e
    return ApiResponse()


@router.post('/transfer', summary="资产转移", dependencies=[Depends(Authority("assets:transfer"))], response_model=ApiResponse[Assets])
async def transfer_asset(request: Request,
                         id: Annotated[int, Form()],
                         location_id: Annotated[int, Form()],
                         owner: Annotated[str, Form()],
                         department_id: Annotated[Union[int, None], Form()] = None,
                         remarks: Annotated[Union[str, None], Form()] = None,
                         session: Session = Depends(get_session_with_transaction), uid: int = Depends(get_uid)):
    """
    资产转移（在不同使用人、不同部门或不同地点之间进行转移）
    :param request: 请求对象
    :param id: 资产ID
    :param location_id: 新位置ID
    :param owner: 新使用人
    :param department_id: 新部门ID
    :param remarks: 备注
    :param session: 数据库会话
    :param uid: 当前用户ID
    :return: API响应
    """
    try:
        current_time = datetime.now()
        # 处理上传的附件
        form_data = await request.form()
        files = []
        for key, value in form_data.multi_items():
            logger.debug(f"Key: {key}, Type: {type(value)}")
            if isinstance(value, StarletteUploadFile):
                files.append(value)
                logger.debug(f"Added file: {value.filename} to files list")
            else:
                logger.debug(f"Value is not UploadFile: {value}")
        logger.debug('upload files: %s', files)
        image_paths = await upload_files(files, settings.upload_dir)
        logger.debug(f"image paths: {image_paths}")

        # 创建资产转移对象
        asset_transfer = AssetsTransfer(
            id=id,
            location_id=location_id,
            department_id=department_id,
            owner=owner,
            remarks=remarks,
            updated_at=current_time,
            status=1,  # 转移后状态保持为已领用
            image_urls=image_paths if image_paths else None
        )

        logger.debug(f"Asset Transfer: {asset_transfer}")
        db_asset = crud.assets.get(session, asset_transfer.id)
        logger.debug(f"db asset: {db_asset}")
        
        # 检查资产状态，只有已领用的资产才能转移
        if db_asset.status != '1':
            return ApiResponse(
                code=500,
                message="该资产未被领用，无法进行转移"
            )
            
        # 记录原始信息用于日志
        previous_owner = db_asset.owner
        previous_department_id = db_asset.department_id
        previous_location_id = db_asset.location_id
        
        # 构建原有使用部门和位置的完整层级路径
        previous_department_full_path = ""
        if previous_department_id:
            previous_department_full_path = build_hierarchical_path(
                session, previous_department_id, crud.assets_department)
                
        previous_location_full_path = ""
        if previous_location_id:
            previous_location_full_path = build_hierarchical_path(
                session, previous_location_id, crud.assets_location)

        # 更新资产信息
        asset_info = crud.assets.update(session, db_asset, asset_transfer)
        
        # 构建新的位置和部门层级路径
        location_full_path = build_hierarchical_path(
            session, asset_info.location_id, crud.assets_location) if asset_info.location_id else ""
        department_full_path = build_hierarchical_path(
            session, asset_info.department_id, crud.assets_department) if asset_info.department_id else ""

        # 构建变更信息用于日志记录
        change_info = {
            "previous_owner": previous_owner,  # 原使用人
            "previous_department": previous_department_full_path,  # 原使用部门
            "previous_location": previous_location_full_path,  # 原位置
            "owner": asset_info.owner,  # 新使用人
            "location": location_full_path or (asset_info.location.name if asset_info.location else ""),  # 新位置
            "department": department_full_path or (asset_info.department.name if asset_info.department else ""),  # 新部门
            "remarks": asset_info.remarks,
            "updated_at": asset_info.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": asset_info.status,
            "asset_name": asset_info.name,
            "asset_code": asset_info.asset_code,
            "category": asset_info.category.name if asset_info.category else "",
            "model": asset_info.model,
            "brand": asset_info.brand,
            "serial_number": asset_info.serial_number
        }
        
        # 记录操作日志
        operator = crud.internal.user.get(session, uid).name
        image_paths_str = json.dumps(image_paths) if image_paths else None
        asset_log = AssetLogs(action="资产转移", asset_id=asset_info.id, details=json.dumps(
            change_info), operator=operator, images=image_paths_str, timestamp=datetime.now())
        crud.assets_logs.insert(session, asset_log)
    except Exception as e:
        logger.error(f"资产转移报错:{str(e)}")
        raise e
    return ApiResponse()


@router.post('/disposal', summary="资产报废", dependencies=[Depends(Authority("assets:disposal"))], response_model=ApiResponse[Assets])
async def disposal_asset(request: Request,
                         asset: Annotated[AssetsDisposal, Form()],
                         session: Session = Depends(
                             get_session_with_transaction),
                         uid: int = Depends(get_uid)):
    """
    资产标记为报废状态
    :param request: 请求对象，用于获取表单数据和文件
    :param asset: 资产报废信息
    :param session: 数据库会话
    :param uid: 用户ID
    :return: API响应
    """
    logger.debug(f"Asset Disposal: {asset}")
    try:
        # 处理文件上传
        form_data = await request.form()
        files = []
        for key, value in form_data.multi_items():
            logger.debug(f"Key: {key}, Type: {type(value)}")
            if isinstance(value, StarletteUploadFile):
                files.append(value)
                logger.debug(f"Added file: {value.filename} to files list")
            else:
                logger.debug(f"Value is not UploadFile: {value}")
        logger.debug('upload files: %s', files)
        image_paths = await upload_files(files, settings.upload_dir)

        db_asset = crud.assets.get(session, asset.id)
        logger.debug(f"db asset: {db_asset}")
        if db_asset.status != '0':
            return ApiResponse(
                code=500,
                message="该资产不在库，无法报废"
            )

        # 创建资产报废对象
        disposal_asset = AssetsDisposal(
            id=asset.id,
            status=3,
            location_id=asset.location_id,
            remarks=asset.remarks,
            image_urls=image_paths if image_paths else None
        )

        asset_info = crud.assets.update(
            session, db_asset, disposal_asset)
        change_info = {
            "location": asset_info.location.name,
            "remarks": asset_info.remarks,
            "status": asset_info.status,
            "asset_name": asset_info.name,
            "asset_code": asset_info.asset_code,
            "category": asset_info.category.name if asset_info.category else "",
            "model": asset_info.model,
            "brand": asset_info.brand,
            "serial_number": asset_info.serial_number
        }
        operator = crud.internal.user.get(session, uid).name
        image_paths_str = json.dumps(image_paths) if image_paths else None
        crud.assets_logs.insert(
            session, AssetLogs(action="资产报废", asset_id=asset.id, details=json.dumps(change_info),
                               operator=operator, images=image_paths_str, timestamp=datetime.now()))
    except Exception as e:
        logger.error(f"资产报废报错:{str(e)}")
        raise e
    return ApiResponse()


@router.post('/import', summary="资产批量导入", dependencies=[Depends(Authority("assets:import"))], response_model=ApiResponse)
async def import_assets(
    file: Annotated[UploadFile, Form(...)],  # 必须上传文件
    session: Session = Depends(get_session_with_transaction),
    uid: int = Depends(get_uid)
):
    """
    资产批量导入接口，资产编号必须携带，只能用于批量导出和导入，不能批量新增
    - 接收一个 `.xlsx` 文件；
    - 根据列名自动解析资产字段；
    - 支持附件上传和日志记录；
    - 支持事务回滚。
    """

    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls")):
        return ApiResponse(code=400, message="只支持 .xls 和 .xlsx 文件")

    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents), na_filter=False)

        required_columns = {
            '资产编号': str,
            '资产名称': str,
            '资产类别': str,
            '存放位置': str,
            '序列号': str,
            '资产型号': str,
            '品牌': str
        }

        optional_columns = {
            '购买日期': 'datetime64[ns]',
            '购买价格': float,
            '财务编码': str,
            '规格': str,
            '备注': str,
            '使用人': str,
            '使用部门': str,
            '状态': str,
            '创建时间': 'datetime64[ns]'
        }

        missing_columns = [
            col for col in required_columns if col not in df.columns]
        if missing_columns:
            return ApiResponse(code=500, message=f"缺少必要列: {missing_columns}")

        # 自动填充可选列
        all_columns = {**required_columns, **optional_columns}
        for col, dtype in all_columns.items():
            if col not in df.columns:
                df[col] = None
            else:
                df[col] = df[col].astype(dtype, errors='ignore')

        # 检查必填列是否为空
        required_data = df[list(required_columns.keys())]
        if required_data.isnull().values.any():
            return ApiResponse(code=500, message="必填项不能为空")

        # 获取所有唯一的资产类别、存放位置和使用部门名称
        unique_categories: list = df['资产类别'].dropna().unique().tolist()
        unique_locations: list = df['存放位置'].dropna().unique().tolist()
        unique_departments: list = df['使用部门'].dropna().unique().tolist() if '使用部门' in df.columns else []

        # 一次性从数据库获取对应对象
        db_categories = crud.assets_category.get_by_names(
            session, unique_categories)

        # 处理层级结构的位置信息
        # 1. 获取所有位置数据
        all_locations = crud.assets_location.get_all(session)
        location_id_mapping = build_hierarchical_path_mapping(all_locations, unique_locations, "位置")
        
        # 处理层级结构的部门信息
        # 1. 获取所有部门数据
        all_departments = crud.assets_department.get_all(session)
        department_id_mapping = build_hierarchical_path_mapping(all_departments, unique_departments, "部门")

        # 构建映射字典
        category_mapping = {cat.name: cat.id for cat in db_categories}
        logger.debug(f"category_mapping: {category_mapping}")

        # 映射 category_id、location_id 和 department_id
        df['category_id'] = df['资产类别'].map(category_mapping)
        df['location_id'] = df['存放位置'].map(location_id_mapping)
        if '使用部门' in df.columns:
            df['department_id'] = df['使用部门'].map(department_id_mapping)
        else:
            df['department_id'] = None
        logger.debug(f"映射后的列名: {df.columns.tolist()}")
        # ================== 修改点5：插入前最终数据校验 ==================
        if df[['category_id', 'location_id']].isnull().any().any():
            invalid_cat = df[df['category_id'].isnull()]['资产类别'].unique()
            invalid_loc = df[df['location_id'].isnull()]['存放位置'].unique()
            invalid_dept = []
            if '使用部门' in df.columns:
                invalid_dept = df[df['department_id'].isnull() & df['使用部门'].notna()]['使用部门'].unique()
            return ApiResponse(
                code=500,
                message=f"映射失败的分类：{invalid_cat}，位置：{invalid_loc}，部门：{invalid_dept}"
            )

        # 处理 purchase_date 等字段
        def parse_date(date_value):
            if date_value is None or pd.isna(date_value):
                return None

            # 如果是pandas的Timestamp类型
            if isinstance(date_value, pd.Timestamp):
                return date_value.to_pydatetime().date()

            # 如果是字符串，尝试解析
            if isinstance(date_value, str):
                try:
                    # 尝试多种常见的日期格式
                    for date_format in ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y', '%m-%d-%Y', '%m/%d/%Y']:
                        try:
                            return datetime.strptime(date_value, date_format).date()
                        except ValueError:
                            continue

                    # 如果上面的格式都不匹配，尝试使用pandas解析
                    return pd.to_datetime(date_value).date()
                except Exception as e:
                    logger.warning(f"无法解析日期 '{date_value}': {str(e)}")
                    return None

            # 如果是datetime对象
            if isinstance(date_value, datetime):
                return date_value.date()

            # 如果是date对象
            if isinstance(date_value, date):
                return date_value

            # 其他情况
            logger.warning(f"未知的日期格式: {type(date_value)}, 值: {date_value}")
            return None

        # 应用日期解析函数
        df['purchase_date'] = df['购买日期'].apply(parse_date)
        logger.debug(f"解析后的购买日期: {df['purchase_date'].tolist()}")
        
        # 处理创建时间字段
        if '创建时间' in df.columns:
            df['created_at_parsed'] = df['创建时间'].apply(parse_date)
        else:
            df['created_at_parsed'] = None
        
        # 处理购买价格字段
        if '购买价格' in df.columns:
            df['purchase_price'] = pd.to_numeric(df['购买价格'], errors='coerce')
        else:
            df['purchase_price'] = None

        # 将资产状态映射为数字
        status_mapping = {
            '在库': '0',
            '使用中': '1',
            '维修中': '2',
            '报废': '3',
            '其他': '4'
        }
        df['状态'] = df['状态'].map(status_mapping).fillna('0')  # 默认状态为 '0'
        # 添加 owner 字段
        df['owner'] = df['使用人'].fillna('').astype(str).replace('', None)

        # 将所有 NaN 替换为 None（防止写入数据库时变成 'nan' 字符串）
        df = df.replace({np.nan: None})
        logger.debug(f"最终数据: {df}")
        for _, row in df.iterrows():
            logger.debug(f"row: {row}")
            # 处理创建时间，如果导入文件中有创建时间则使用，否则使用当前时间
            created_time = datetime.now()
            if row.get('created_at_parsed') is not None:
                if isinstance(row['created_at_parsed'], date):
                    created_time = datetime.combine(row['created_at_parsed'], datetime.min.time())
                elif isinstance(row['created_at_parsed'], datetime):
                    created_time = row['created_at_parsed']
            
            asset = Assets(
                name=row['资产名称'],
                asset_code=row['资产编号'].strip(),
                category_id=row['category_id'],
                location_id=row['location_id'],
                serial_number=row['序列号'],
                model=row['资产型号'],
                brand=row['品牌'],
                purchase_date=row['purchase_date'],
                purchase_price=row.get('purchase_price'),
                financial_code=row.get('财务编码'),
                specifications=row.get('规格'),
                remarks=row.get('备注'),
                department_id=row.get('department_id'),
                created_at=created_time,
                updated_at=datetime.now(),
                owner=row.get('使用人'),
                status=row.get('状态', '0')  # 默认状态为 '0'
            )
            # assets.append(asset)
            logger.debug(f"asset: {asset}")
            asset = crud.assets.insert(session, asset)

            change_info = jsonable_encoder(asset)
            change_info['location'] = asset.location.name
            change_info['category'] = asset.category.name
            operator = crud.internal.user.get(session, uid).name
            crud.assets_logs.insert(
                session, AssetLogs(action="资产录入", asset_id=asset.id,
                                   details=json.dumps(change_info),
                                   operator=operator, timestamp=datetime.now()))

        return ApiResponse()
    except IntegrityError as e:
        session.rollback()
        logger.error(f"Duplicate Error: {str(e)}")
        return ApiResponse(code=500, message=str(e))

    except Exception as e:
        session.rollback()
        logger.error(f"Asset Import Error: {str(e)}")
        return ApiResponse(code=500, message=str(e))


@router.get('/export', summary="资产批量导出", dependencies=[Depends(Authority("assets:export"))])
async def export_assets(session: Session = Depends(get_session)):
    """
    资产批量导出接口。
    - 返回与资产导入模板一致的 `.xlsx` 文件；
    - 包含所有资产信息；
    - 支持浏览器直接下载。
    """
    try:
        # 查询所有资产数据
        assets = crud.assets.get_all(session)

        # 构建 DataFrame
        data = []
        for asset in assets:
            # 构建完整的位置路径
            location_full_path = build_location_full_path(
                session, asset.location_id) if asset.location_id else None
            
            # 构建完整的部门层级路径
            department_full_path = build_hierarchical_path(
                session, asset.department_id, crud.assets_department) if asset.department_id else None

            data.append({
                '资产编号': asset.asset_code,
                '资产名称': asset.name,
                '资产类别': asset.category.name if asset.category else None,
                '存放位置': location_full_path or (asset.location.name if asset.location else None),
                '序列号': asset.serial_number,
                '资产型号': asset.model,
                '品牌': asset.brand,
                '购买日期': asset.purchase_date,
                '购买价格': asset.purchase_price,
                '财务编码': asset.financial_code,
                '规格': asset.specifications,
                '使用人': asset.owner,
                '使用部门': department_full_path or (asset.department.name if asset.department else None),
                '状态': asset.status,
                '创建时间': asset.created_at,
                '备注': asset.remarks,
            })

        df = pd.DataFrame(data)
        # 添加状态映射
        status_mapping = {
            '0': '在库',
            '1': '使用中',
            '2': '维修中',
            '3': '报废',
            '4': '其他'
        }
        df['状态'] = df['状态'].map(status_mapping).fillna('未知状态')

        # 生成 Excel 文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Assets')

        output.seek(0)

        # 返回文件流
        return StreamingResponse(
            output,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                "Content-Disposition": "attachment; filename=assets_export.xlsx"}
        )

    except Exception as e:
        logger.error(f"Asset Export Error: {str(e)}")
        return ApiResponse(code=500, message=str(e))


@router.get('/{id}', summary="通过资产ID获取资产信息", dependencies=[Depends(Authority("assets:read"))], response_model=ApiResponse)
async def get_asset_by_id(id: int, session: Session = Depends(get_session)):
    """
    通过资产ID获取资产信息，包含分类和位置详细信息
    :param id:
    :param session:
    :return:
    """
    try:
        result = crud.assets.get_with_details(session, id)
        if not result:
            return ApiResponse(code=404, message="资产不存在")

        asset, category, location, department = result

        # 构建完整的位置路径
        location_name = ""
        if location:
            location_name = build_location_full_path(session, location.id)

        # 构建完整的部门路径
        department_name = ""
        if department:
            department_name = build_hierarchical_path(
                session, department.id, crud.assets_department)

        # 构建响应数据
        asset_data = {
            **asset.model_dump(),
            "category_name": category.name if category else None,
            "location_name": location_name if location_name else None,
            "department_name": department_name if department_name else None,
        }

        return ApiResponse(data=asset_data)
    except Exception as e:
        logger.error(f"Get Asset Error:{str(e)}")
        return ApiResponse(
            code=500,
            message=str(e)
        )
