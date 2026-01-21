import datetime
import json
import os
import pandas as pd
import numpy as np
from fastapi import APIRouter, Depends, Form, Request, UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, desc
from io import BytesIO
from loguru import logger
from typing import List, Union, Tuple, Annotated, Optional
from datetime import datetime, date
from app.common.utils import Tree, upload_files, build_hierarchical_path
from app.common.response_code import ApiResponse, SearchResponse
from app.common.auth_casbin import Authority
from app.common.database import get_session, get_session_with_transaction
from app.common.dep import get_uid
from app.models.assets import Assets, AssetLogs, \
    AssetWithInventoryStatusAndAction, InventoryRecords, InventoryBatches, \
    InventoryBatchCreate, InventoryBatchUpdate, InventoryBatchSearch, InventoryRecordSearch, InventoryRecordWithDetails, InventoryAssetsSearch
from app.models.internal import Pagination
from app import crud
from app.settings import settings


def calculate_inventory_status_with_action(session: Session, asset: Assets, batch_id: Union[int, None] = None) -> tuple[int, Union[str, None]]:
    """
    动态计算资产的盘点状态和最新的action_type
    :param session: 数据库会话
    :param asset: 资产对象
    :param batch_id: 指定的盘点批次ID，如果为None则使用当前活动批次
    :return: (盘点状态, 最新action_type) 盘点状态: 0-未盘点，1-已盘点

    业务逻辑说明：
    - 未盘点(0)：在指定批次中没有任何盘点记录
    - 已盘点(1)：在指定批次中有任何类型的盘点记录（包括CONFIRM_IN_PLACE、INFO_UPDATE、NEW_ASSET、EXCEPTION）
    """
    target_batch_id = batch_id

    # 如果没有指定批次ID，则获取当前活动的盘点批次
    if target_batch_id is None:
        active_batch = crud.inventory_batches.get_active_batch(session)
        if not active_batch:
            # 如果没有活动的盘点批次，则无法进行盘点状态查询
            # 这种情况下应该返回未盘点状态，因为没有进行中的盘点任务
            return 0, None  # 未盘点，无action_type
        target_batch_id = active_batch.batch_id

    # 检查该资产在指定批次中的所有盘点记录，按时间倒序排列
    inventory_record_stmt = select(InventoryRecords).where(
        and_(
            InventoryRecords.asset_id == asset.id,
            InventoryRecords.batch_id == target_batch_id
        )
    ).order_by(desc(InventoryRecords.scanned_at))

    inventory_records = session.exec(inventory_record_stmt).all()

    if not inventory_records:
        return 0, None  # 未盘点，无action_type

    # 获取最新的盘点记录
    latest_record = inventory_records[0]
    latest_action_type = latest_record.action_type

    # 根据最新盘点记录的action_type判断状态
    # 只要有盘点记录，就认为是已盘点（包括异常情况）
    if latest_record.action_type in ["CONFIRM_IN_PLACE", "INFO_UPDATE", "NEW_ASSET", "EXCEPTION"]:
        return 1, latest_action_type  # 已盘点（包含所有类型的盘点记录）
    else:
        # 对于未知的action_type，默认认为是已盘点
        return 1, latest_action_type


router = APIRouter()


@router.post("/search/inventory-assets", summary="查找盘点资产", dependencies=[Depends(Authority("assets:read"))], response_model=ApiResponse[SearchResponse[AssetWithInventoryStatusAndAction]])
async def search_inventory_assets(search: Pagination[InventoryAssetsSearch], session: Session = Depends(get_session)):
    """
    查找盘点资产接口
    支持通过asset_code、inventory_status、last_inventory_batch_id字段查询盘点资产列表
    已优化：在数据库层面排除报废状态的资产并进行分页，大幅提升查询性能

    盘点状态说明：
    - 0: 未盘点
    - 1: 已盘点（当选择此状态时，会同时包含正常已盘点和异常状态的资产）
    - 2: 异常（仅显示异常状态的资产）
    """
    logger.debug(f"search inventory assets: {search}")

    # 构建过滤条件
    filter_type = {"asset_code": "like"}

    def build_asset_response(asset_data_list, total_count):
        """构建统一的响应数据"""
        assets_with_inventory_status: List[AssetWithInventoryStatusAndAction] = [
        ]

        for item in asset_data_list:
            if len(item) == 3:  # (asset, category, location)
                asset, category, location = item
                department = None
                # 计算盘点状态和最新action_type
                inventory_status, latest_action_type = calculate_inventory_status_with_action(
                    session, asset, search.search.last_inventory_batch_id
                )
            elif len(item) == 4 and isinstance(item[3], int):  # (asset, category, location, inventory_status)
                asset, category, location, inventory_status = item
                department = None
                # 获取最新action_type
                _, latest_action_type = calculate_inventory_status_with_action(
                    session, asset, search.search.last_inventory_batch_id
                )
            else:  # (asset, category, location, department)
                asset, category, location, department = item
                # 计算盘点状态和最新action_type
                inventory_status, latest_action_type = calculate_inventory_status_with_action(
                    session, asset, search.search.last_inventory_batch_id
                )

            # 构建完整的位置路径
            location_full_path = build_hierarchical_path(
                session, asset.location_id, crud.assets_location)

            asset_with_inventory = AssetWithInventoryStatusAndAction(
                **asset.model_dump(),
                category_name=category.name if category else None,
                location_name=location_full_path or (location.name if location else None),
                department_name=department.name if department else None,
                inventory_status=inventory_status,
                latest_action_type=latest_action_type
            )
            assets_with_inventory_status.append(asset_with_inventory)

        return ApiResponse(data={"total": total_count, "data": assets_with_inventory_status})

    # 如果没有指定盘点状态和操作类型过滤，可以直接使用数据库分页
    if search.search.inventory_status is None and search.search.action_type is None:
        # 获取总数（排除报废状态）
        total = crud.assets.search_inventory_assets_total(
            session, search.search, filter_type)

        # 获取分页数据（排除报废状态）
        paginated_assets = crud.assets.search_inventory_assets(
            session, search, filter_type)

        return build_asset_response(paginated_assets, total)

    else:
        # 如果指定了盘点状态过滤，需要获取所有数据进行过滤
        # 首先获取总数
        total_count = crud.assets.search_inventory_assets_total(
            session, search.search, filter_type)

        # 获取所有符合基础条件的资产数据
        extended_search = Pagination(
            search=search.search,
            page=1,
            page_size=total_count if total_count > 0 else 1000  # 获取所有数据
        )

        all_assets = crud.assets.search_inventory_assets(
            session, extended_search, filter_type)

        # 根据盘点状态和操作类型进行过滤
        filtered_assets = []
        for asset, category, location, department in all_assets:
            # 计算盘点状态和最新action_type
            inventory_status, latest_action_type = calculate_inventory_status_with_action(
                session, asset, search.search.last_inventory_batch_id
            )

            # 盘点状态过滤
            status_match = True
            if search.search.inventory_status is not None:
                status_match = inventory_status == search.search.inventory_status

            # 操作类型过滤
            action_match = True
            if search.search.action_type is not None:
                action_match = latest_action_type == search.search.action_type

            # 同时满足盘点状态和操作类型过滤条件
            if status_match and action_match:
                filtered_assets.append(
                    (asset, category, location, inventory_status))

        # 计算总数（这里是近似值，实际应用中可以考虑缓存或其他优化方案）
        total = len(filtered_assets)

        # 手动分页
        start_index = (search.page - 1) * search.page_size
        end_index = start_index + search.page_size
        paginated_assets = filtered_assets[start_index:end_index]

        return build_asset_response(paginated_assets, total)


@router.post('/inventory/batches', summary="创建盘点批次", dependencies=[Depends(Authority("assets:write"))], response_model=ApiResponse[InventoryBatches])
async def create_inventory_batch(batch_data: InventoryBatchCreate, session: Session = Depends(get_session), user_id: int = Depends(get_uid)):
    """
    创建新的盘点批次
    同一时间只允许一个盘点批次状态为active
    """
    logger.debug(f"create inventory batch: {batch_data}")

    try:
        # 构建盘点批次对象
        batch = InventoryBatches(
            batch_name=batch_data.batch_name,
            start_date=batch_data.start_date,
            end_date=batch_data.end_date,
            created_by_user_id=user_id,
            status="active"
        )

        # 使用CRUD方法创建，包含业务逻辑验证
        success, message, created_batch = crud.inventory_batches.create_with_validation(
            session, batch)

        if not success:
            return ApiResponse(code=400, message=message)

        return ApiResponse(data=created_batch, message=message)

    except Exception as e:
        logger.error(f"Create Inventory Batch Error: {str(e)}")
        session.rollback()
        return ApiResponse(code=500, message=f"创建盘点批次失败: {str(e)}")


@router.post('/inventory/batches/search', summary="获取盘点批次列表", dependencies=[Depends(Authority("assets:read"))], response_model=ApiResponse)
async def get_inventory_batches(search: Pagination[InventoryBatchSearch], session: Session = Depends(get_session)):
    """
    获取盘点批次列表（分页）
    """
    logger.debug(f"search inventory batches: {search}")

    # 定义搜索字段的过滤类型
    filter = {
        "batch_name": "like",
        "status": "eq",
        "created_by_user_id": "eq",
        "start_date": "ge",
        "end_date": "le"
    }

    try:
        # 获取总数
        total = crud.inventory_batches.search_total(
            session, search.search, filter)
        logger.debug(f'search inventory batches total: {total}')

        # 获取分页数据
        batches = crud.inventory_batches.search(
            session, search, filter, order_col='created_at')
        logger.debug(f'search inventory batches: {batches}')

        return ApiResponse(data={"total": total, "data": batches})
    except Exception as e:
        logger.error(f"Get Inventory Batches Error: {str(e)}")
        return ApiResponse(code=500, message=f"获取盘点批次列表失败: {str(e)}")


@router.get('/inventory/batches/latest', summary="获取最新盘点批次", dependencies=[Depends(Authority("assets:read"))], response_model=ApiResponse[InventoryBatches], deprecated=True)
async def get_latest_inventory_batch(session: Session = Depends(get_session)):
    """
    获取最新的盘点批次
    返回最新创建的盘点批次，如果没有则返回null
    """
    logger.debug("get latest inventory batch")

    try:
        # 使用CRUD方法获取最新批次
        latest_batch = crud.inventory_batches.get_latest_batch(session)

        if not latest_batch:
            return ApiResponse(data=None, message="没有找到盘点批次")

        return ApiResponse(data=latest_batch, message="获取最新盘点批次成功")

    except Exception as e:
        logger.error(f"Get Latest Inventory Batch Error: {str(e)}")
        return ApiResponse(code=500, message=f"获取最新盘点批次失败: {str(e)}")


@router.put('/inventory/batches/{batch_id}', summary="更新盘点批次", dependencies=[Depends(Authority("assets:write"))], response_model=ApiResponse[InventoryBatches])
async def update_inventory_batch(batch_id: int, batch_data: InventoryBatchUpdate, session: Session = Depends(get_session)):
    """
    更新盘点批次信息
    """
    logger.debug(f"update inventory batch {batch_id}: {batch_data}")

    try:
        # 获取现有批次对象
        db_obj = crud.inventory_batches.get(session, batch_id)
        if not db_obj:
            return ApiResponse(code=404, message="盘点批次不存在")

        # 使用CRUD基类的标准更新方法
        updated_batch = crud.inventory_batches.update(
            session, db_obj, batch_data)

        return ApiResponse(data=updated_batch, message="盘点批次更新成功")
    except Exception as e:
        logger.error(f"Update Inventory Batch Error: {str(e)}")
        session.rollback()
        return ApiResponse(code=500, message=f"更新盘点批次失败: {str(e)}")


@router.delete('/inventory/batches/{batch_id}', summary="删除盘点批次", dependencies=[Depends(Authority("assets:delete"))], response_model=ApiResponse)
async def delete_inventory_batch(batch_id: int, session: Session = Depends(get_session)):
    """
    删除盘点批次
    注意：如果批次下存在盘点记录，则不允许删除
    """
    try:
        # 查找批次
        batch = crud.inventory_batches.get(session, batch_id)
        if not batch:
            return ApiResponse(code=404, message="盘点批次不存在")

        # 检查是否存在盘点记录
        records = crud.inventory_records.get_records_by_batch(
            session, batch_id)
        if records:
            return ApiResponse(code=400, message="该盘点批次下存在盘点记录，无法删除")

        # 删除批次
        crud.inventory_batches.delete(session, batch_id)

        return ApiResponse(message="盘点批次删除成功")
    except Exception as e:
        logger.error(f"Delete Inventory Batch Error: {str(e)}")
        session.rollback()
        return ApiResponse(code=500, message=f"删除盘点批次失败: {str(e)}")


@router.post('/inventory/records', summary="创建盘点记录", dependencies=[Depends(Authority("assets:write"))], response_model=ApiResponse[InventoryRecords])
async def create_inventory_record(
    request: Request,
    batch_id: Annotated[int, Form()],
    action_type: Annotated[str, Form()],
    asset_id: Annotated[Union[int, None], Form()] = None,  # 新资产时可为空
    actual_status: Annotated[Union[str, None], Form()] = None,
    actual_location_id: Annotated[Union[int, None], Form()] = None,
    actual_owner: Annotated[Union[str, None], Form()] = None,
    remarks: Annotated[Union[str, None], Form()] = None,
    # 新资产创建参数（仅当action_type为NEW_ASSET时使用）
    name: Annotated[Union[str, None], Form()] = None,
    category_id: Annotated[Union[int, None], Form()] = None,
    location_id: Annotated[Union[int, None], Form()] = None,
    serial_number: Annotated[Union[str, None], Form()] = None,
    model: Annotated[Union[str, None], Form()] = None,
    brand: Annotated[Union[str, None], Form()] = None,
    purchase_date: Annotated[Union[date, None], Form()] = None,
    financial_code: Annotated[Union[str, None], Form()] = None,
    specifications: Annotated[Union[str, None], Form()] = None,
    asset_remarks: Annotated[Union[str, None], Form()] = None,  # 资产备注，区别于盘点备注
    session: Session = Depends(get_session_with_transaction),
    user_id: int = Depends(get_uid)
):
    """
    创建盘点记录
    支持图片上传，图片通过form-data方式提交

    功能说明：
    1. 普通盘点记录：提供asset_id和action_type（CONFIRM_IN_PLACE、INFO_UPDATE、EXCEPTION）
    2. 盘点发现新资产：action_type设为NEW_ASSET，同时提供新资产创建参数

    新资产创建必填参数：
    - name: 资产名称
    - category_id: 资产分类ID
    - location_id: 资产位置ID
    - serial_number: 序列号
    - model: 设备型号
    - brand: 品牌

    新资产创建可选参数：
    - purchase_date: 购买日期
    - financial_code: 财务编码
    - specifications: 规格
    - asset_remarks: 资产备注（区别于盘点备注remarks）

    注意：当action_type为NEW_ASSET时，asset_id可为空，系统会自动创建新资产并关联盘点记录
    """
    # 记录用户提交的参数，方便调试
    if action_type == "NEW_ASSET":
        logger.info(f"创建盘点记录[NEW_ASSET] - 用户ID:{user_id}, 批次ID:{batch_id}, 资产名称:{name}, 分类ID:{category_id}, 位置ID:{location_id}, 序列号:{serial_number}, 型号:{model}, 品牌:{brand}, 购买日期:{purchase_date}, 财务编码:{financial_code}, 规格:{specifications}, 资产备注:{asset_remarks}, 实际状态:{actual_status}, 实际位置ID:{actual_location_id}, 实际负责人:{actual_owner}, 盘点备注:{remarks}")
    else:
        logger.info(
            f"创建盘点记录[{action_type}] - 用户ID:{user_id}, 批次ID:{batch_id}, 资产ID:{asset_id}, 实际状态:{actual_status}, 实际位置ID:{actual_location_id}, 实际负责人:{actual_owner}, 盘点备注:{remarks}")

    try:
        # 验证盘点批次是否存在
        batch = crud.inventory_batches.get(session, batch_id)
        if not batch:
            return ApiResponse(code=404, message="盘点批次不存在")

        # 处理新资产创建
        if action_type == "NEW_ASSET":
            # 验证新资产必填参数
            if not all([name, category_id, location_id, serial_number, model, brand]):
                return ApiResponse(code=400, message="新建资产时，资产名称、分类ID、位置ID、序列号、型号、品牌为必填项")

            # 创建新资产
            current_time = datetime.now()
            new_asset = Assets(
                name=name,
                category_id=category_id,
                location_id=location_id,
                serial_number=serial_number,
                model=model,
                brand=brand,
                purchase_date=purchase_date,
                financial_code=financial_code,
                specifications=specifications,
                remarks=asset_remarks,
                created_at=current_time,
                updated_at=current_time,
                status='0'  # 新建资产默认状态为在库
            )
            # 生成资产编码
            new_asset.asset_code = crud.assets.generate_asset_code(
                session, settings.asset_prefix)

            # 插入新资产到数据库
            asset = crud.assets.insert(session, new_asset)
            asset_id = asset.id

            # 新资产创建时的日志将在后续的NEW_ASSET分支中统一处理
        else:
            # 验证现有资产是否存在
            if not asset_id:
                return ApiResponse(code=400, message="非新建资产时，asset_id为必填项")

            asset = crud.assets.get(session, asset_id)
            if not asset:
                return ApiResponse(code=404, message="资产不存在")

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
        logger.debug(f"image paths: {image_paths}")

        # 根据action_type构建details字典，只保存变动信息
        details_dict = {}
        asset_updated = False
        log_created = False

        if action_type == "INFO_UPDATE":
            # 信息更新：只记录变更的字段
            if actual_location_id and actual_location_id != asset.location_id:
                # 获取位置名称用于日志记录
                old_location = crud.assets_location.get(
                    session, asset.location_id)
                new_location = crud.assets_location.get(
                    session, actual_location_id)
                details_dict["location"] = {
                    "from": old_location.name if old_location else None,
                    "to": new_location.name if new_location else None
                }

            if actual_owner and actual_owner != asset.owner:
                details_dict["owner"] = {
                    "from": asset.owner,
                    "to": actual_owner
                }

            if actual_status and actual_status in ['0', '1', '2', '3', '4'] and actual_status != asset.status:
                # 状态映射
                status_map = {'0': '正常', '1': '维修中',
                              '2': '报废', '3': '丢失', '4': '借出'}
                details_dict["status"] = {
                    "from": status_map.get(asset.status, asset.status),
                    "to": status_map.get(actual_status, actual_status)
                }

            if remarks and remarks != asset.remarks:
                details_dict["remarks"] = {
                    "from": asset.remarks,
                    "to": remarks
                }

        elif action_type == "NEW_ASSET":
            # 新增资产：只记录初始设置的关键信息
            if actual_location_id:
                location = crud.assets_location.get(
                    session, actual_location_id)
                details_dict["location"] = {
                    "to": location.name if location else None}

            if actual_owner:
                details_dict["owner"] = {"to": actual_owner}

            # 记录资产分类信息
            if hasattr(asset, 'category') and asset.category:
                details_dict["category"] = {"to": asset.category.name}

        elif action_type == "EXCEPTION":
            # 异常情况：记录异常描述
            if remarks:
                details_dict["description"] = remarks
                # 可以根据关键词判断异常严重程度
                if any(keyword in remarks for keyword in ["丢失", "遗失", "损坏", "无法找到"]):
                    details_dict["severity"] = "high"
                else:
                    details_dict["severity"] = "medium"

        # CONFIRM_IN_PLACE 类型不需要记录额外信息，details_dict 保持为空

        # 如果没有任何详细信息，则设为None
        if not details_dict:
            details_dict = None

        # 创建盘点记录（此时details_dict已经完整）
        record = InventoryRecords(
            asset_id=asset_id,
            batch_id=batch_id,
            scanned_by_user_id=user_id,
            action_type=action_type,
            actual_location_id=actual_location_id,
            actual_user=actual_owner,
            photo_urls=image_paths,
            details=details_dict
        )
        record = crud.inventory_records.insert(session, record)

        # 所有盘点操作都需要更新资产的盘点时间和盘点批次
        asset.last_inventory_time = record.scanned_at
        asset.last_inventory_batch_id = batch_id
        asset.updated_at = datetime.now()
        # 盘点基础信息更新，所有操作都需要保存
        asset_updated = True
        logger.debug(
            f"更新资产盘点信息 - 资产ID: {asset_id}, 盘点时间: {record.scanned_at}, 批次ID: {batch_id}")

        # 获取操作人姓名
        operator = crud.internal.user.get(session, user_id).name

        # 根据action_type执行不同的业务逻辑
        if action_type == "INFO_UPDATE":
            # 信息更新：更新资产信息
            info_updated = False

            if actual_location_id and actual_location_id != asset.location_id:
                asset.location_id = actual_location_id
                info_updated = True

            if actual_owner and actual_owner != asset.owner:
                # 直接使用actual_owner作为用户名
                asset.owner = actual_owner
                info_updated = True

            if remarks and remarks != asset.remarks:
                # 更新资产备注信息
                asset.remarks = remarks
                info_updated = True

            # 处理资产状态变更
            if actual_status and actual_status in ['0', '1', '2', '3', '4'] and actual_status != asset.status:
                asset.status = actual_status
                info_updated = True

            # 只有当有实际变更时才创建资产变更日志
            if info_updated and details_dict:
                asset_log = AssetLogs(
                    asset_id=asset_id,
                    operator=operator,
                    action="盘点信息更新",
                    details=json.dumps(
                        details_dict, ensure_ascii=False),
                    images=",".join(image_paths) if image_paths else None,
                    timestamp=record.scanned_at
                )
                crud.assets_logs.insert(session, asset_log)
                log_created = True

        elif action_type == "EXCEPTION":
            # 异常情况：写入资产日志记录异常
            # 如果有异常描述，同步更新资产的备注信息
            if remarks and remarks != asset.remarks:
                asset.remarks = remarks
                asset_updated = True
                logger.debug(f"更新资产异常备注 - 资产ID: {asset_id}, 新备注: {remarks}")

            # 异常情况总是需要记录日志
            asset_log = AssetLogs(
                asset_id=asset_id,
                operator=operator,
                action="盘点异常",
                details=json.dumps(
                    details_dict, ensure_ascii=False) if details_dict else None,
                images=",".join(image_paths) if image_paths else None,
                timestamp=record.scanned_at
            )
            crud.assets_logs.insert(session, asset_log)
            log_created = True

        elif action_type == "CONFIRM_IN_PLACE":
            # 在位确认：写入简单的确认日志
            asset_log = AssetLogs(
                asset_id=asset_id,
                operator=operator,
                action="盘点在位确认",
                details=None,  # 在位确认不需要详细信息
                images=",".join(image_paths) if image_paths else None,
                timestamp=record.scanned_at
            )
            crud.assets_logs.insert(session, asset_log)
            log_created = True

        elif action_type == "NEW_ASSET":
            # 新增资产：创建盘点新建资产日志，使用简化的details
            asset_log = AssetLogs(
                asset_id=asset_id,
                operator=operator,
                action="盘点新建资产",
                details=json.dumps(
                    details_dict, ensure_ascii=False) if details_dict else None,
                images=",".join(image_paths) if image_paths else None,
                timestamp=record.scanned_at
            )
            crud.assets_logs.insert(session, asset_log)
            log_created = True

        # 保存资产更新
        if asset_updated:
            session.add(asset)

        # 构建返回消息
        message_parts = ["盘点记录创建成功"]
        if action_type == "NEW_ASSET":
            message_parts.append(f"新资产已创建（编号：{asset.asset_code}）")
        if asset_updated:
            message_parts.append("资产信息已更新")
        if log_created:
            message_parts.append("资产日志已记录")

        return ApiResponse(data=record, message="，".join(message_parts))
    except Exception as e:
        logger.error(f"Create Inventory Record Error: {str(e)}")
        return ApiResponse(code=500, message=f"创建盘点记录失败: {str(e)}")


@router.post('/inventory/records/search', summary="获取盘点记录列表", dependencies=[Depends(Authority("assets:read"))], response_model=ApiResponse)
async def get_inventory_records(search: Pagination[InventoryRecordSearch], session: Session = Depends(get_session)):
    """
    获取盘点记录列表（分页，带详细信息）
    """
    logger.debug(f"search inventory records: {search}")

    # 定义搜索字段的过滤类型
    filter = {
        "asset_id": "eq",
        "batch_id": "eq",
        "action_type": "eq",
        "scanned_by_user_id": "eq"
    }

    try:
        # 获取总数
        total = crud.inventory_records.search_total(
            session, search.search, filter)
        logger.debug(f'search inventory records total: {total}')

        # 获取分页数据（带详细信息）
        records = crud.inventory_records.search_with_details(
            session, search, filter)
        logger.debug(f'search inventory records: {len(records)} records found')

        return ApiResponse(data={"total": total, "data": records})
    except Exception as e:
        logger.error(f"Get Inventory Records Error: {str(e)}")
        return ApiResponse(code=500, message=f"获取盘点记录列表失败: {str(e)}")


@router.get('/inventory/batches/{batch_id}/records', summary="获取指定批次的盘点记录", dependencies=[Depends(Authority("assets:read"))], response_model=SearchResponse[InventoryRecordWithDetails])
async def get_batch_inventory_records(batch_id: int, page: int = 1, size: int = 20, session: Session = Depends(get_session)):
    """
    获取指定盘点批次的所有盘点记录
    """
    try:
        # 验证批次是否存在
        batch = crud.inventory_batches.get(session, batch_id)
        if not batch:
            return SearchResponse(code=404, message="盘点批次不存在")

        # 构建搜索参数
        search_query = InventoryRecordSearch(batch_id=batch_id)
        search = Pagination(query=search_query, page=page, size=size)

        # 调用通用的获取记录方法
        return await get_inventory_records(search, session)
    except Exception as e:
        logger.error(f"Get Batch Inventory Records Error: {str(e)}")
        return SearchResponse(code=500, message=f"获取批次盘点记录失败: {str(e)}")


@router.get('/inventory/batches/{batch_id}/summary', summary="获取盘点批次统计信息", dependencies=[Depends(Authority("assets:read"))], response_model=ApiResponse)
async def get_inventory_batch_summary(batch_id: int, session: Session = Depends(get_session)):
    """
    获取盘点批次的统计信息
    """
    try:
        # 使用CRUD方法获取统计信息
        summary = crud.inventory_batches.get_batch_statistics(
            session, batch_id)
        if not summary:
            return ApiResponse(code=404, message="盘点批次不存在")

        return ApiResponse(data=summary, message="获取盘点批次统计信息成功")
    except Exception as e:
        logger.error(f"Get Inventory Batch Summary Error: {str(e)}")
        return ApiResponse(code=500, message=f"获取盘点批次统计信息失败: {str(e)}")


@router.get('/inventory/records', summary="检查资产是否已盘点", dependencies=[Depends(Authority("assets:read"))], response_model=ApiResponse)
async def check_asset_inventory_status(asset_id: int, batch_id: int, session: Session = Depends(get_session)):
    """
    检查指定资产在特定批次中是否已经盘点过
    """
    try:
        # 验证资产是否存在
        asset = crud.assets.get(session, asset_id)
        if not asset:
            return ApiResponse(code=404, message="资产不存在")

        # 验证批次是否存在
        batch = crud.inventory_batches.get(session, batch_id)
        if not batch:
            return ApiResponse(code=404, message="盘点批次不存在")

        # 检查是否已经盘点过
        is_inventoried = crud.inventory_records.check_asset_inventory_status(
            session, asset_id, batch_id)

        return ApiResponse(
            data={"is_inventoried": is_inventoried},
            message="查询成功"
        )
    except Exception as e:
        logger.error(f"Check Asset Inventory Status Error: {str(e)}")
        return ApiResponse(code=500, message=f"查询资产盘点状态失败: {str(e)}")


@router.get('/inventory/log/{asset_id}', summary="获取资产盘点日志", dependencies=[Depends(Authority("assets:read"))], response_model=ApiResponse)
async def get_asset_inventory_logs(
    asset_id: int,
    batch_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    session: Session = Depends(get_session)
):
    """
    获取指定资产的盘点日志记录
    支持按盘点批次和时间范围筛选

    参数说明：
    - asset_id: 资产ID（必填）
    - batch_id: 盘点批次ID（可选）
    - start_date: 开始时间（可选）
    - end_date: 结束时间（可选）
    """
    try:
        # 验证资产是否存在
        asset = crud.assets.get(session, asset_id)
        if not asset:
            return ApiResponse(code=404, message="资产不存在")

        # 处理时间参数：将date转换为datetime
        scanned_at_from = None
        scanned_at_to = None

        if start_date:
            # start_date设为当天凌晨0点
            scanned_at_from = datetime.combine(start_date, datetime.min.time())

        if end_date:
            # end_date设为当天晚上23:59:59
            scanned_at_to = datetime.combine(end_date, datetime.max.time())

        # 构建搜索条件
        search_conditions = InventoryRecordSearch(
            asset_id=asset_id,
            batch_id=batch_id,
            scanned_at_from=scanned_at_from,
            scanned_at_to=scanned_at_to
        )

        # 定义搜索字段的过滤类型
        filter_type = {
            "asset_id": "eq",
            "batch_id": "eq",
            "action_type": "eq",
            "scanned_by_user_id": "eq"
        }

        # 直接获取所有符合条件的盘点记录（不使用分页）
        records = crud.inventory_records.get_inventory_logs_without_pagination(
            session, search_conditions, filter_type)

        logger.debug(
            f'Asset {asset_id} inventory logs: {len(records)} records found')

        return ApiResponse(
            data=records,
            message=f"获取资产盘点日志成功，共{len(records)}条记录"
        )

    except Exception as e:
        logger.error(f"Get Asset Inventory Logs Error: {str(e)}")
        return ApiResponse(code=500, message=f"获取资产盘点日志失败: {str(e)}")
