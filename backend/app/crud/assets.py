from typing import Union, Optional, Dict, List, Any
from pydantic import BaseModel
from datetime import datetime, date, timedelta
from loguru import logger
from sqlmodel import select, Session, delete, desc, func, join, or_, and_
from sqlalchemy.orm.exc import NoResultFound
from ..models.assets import Assets, AssetsCategory, AssetsLocation, AssetsDepartment, AssetLogs, InventoryBatches, InventoryRecords, InventoryRecordWithDetails
from .base import CRUDBase, CRUDCategory
from ..models.internal import Pagination


class CRUDAssets(CRUDBase[Assets]):

    def get_max_asset_code(self, session: Session, prefix: str = "AST") -> Optional[str]:
        """
        获取当前最大的资产编号
        :param session:
        :param prefix: 资产编号前缀
        :return:
        """
        year = datetime.now().strftime("%Y")
        sql = select(self.model).where(self.model.asset_code.startswith(f"{prefix}{year}")).order_by(
            desc(self.model.asset_code))
        last_asset = session.exec(sql).first()
        if last_asset and last_asset.asset_code:
            return last_asset.asset_code
        return None

    def generate_asset_code(self, session: Session, prefix: str = "AST") -> str:
        """
        生成资产编号
        :param session:
        :param prefix: 资产编号前缀
        :return:
        """
        current_max_code = self.get_max_asset_code(session, prefix)
        if current_max_code is not None:
            last_number = int(current_max_code[-4:])
            new_number = last_number + 1
        else:
            new_number = 1
        year = datetime.now().strftime("%Y")
        asset_code = f"{prefix}{year}{new_number:04}"
        return asset_code

    def search_total(self, session: Session, q: BaseModel, filter_type: Optional[Dict[str, str]] = None):
        """
        每次进行分页查询的时候，都需要返回一个total值，表示对应搜索，现阶段数据库有多少内容，便于前端分页数
        :param session:
        :param q:
        :param filter_type: 字段过滤形式
        :return:
        """
        sql = select(func.count(self.model.id))
        sql = sql.join(AssetsCategory, isouter=True)  # 左关联 AssetsCategory
        sql = sql.join(AssetsLocation, isouter=True)  # 左关联 AssetsLocation
        sql = sql.join(AssetsDepartment, isouter=True)  # 左关联 AssetsDepartment
        sql = self._make_search(sql, q, filter_type)
        logger.debug(str(sql))
        try:
            result = session.exec(sql).one()
        except NoResultFound:
            result = 0
        return result

    def search(self, session: Session, search: Pagination, filter_type: Optional[Dict[str, str]] = None,
               columns: Optional[List] = None, order_col: Optional[str] = 'id'):
        """
        分页查询方法
        :param session:
        :param search: Pagination实例对象，包含各搜索参数
        :param filter_type: 指定的各属性值判断形式
        :param columns: 查询返回指定columns
        :param order_col: order排序列名，默认id，此col需要为自增id
        :return:
        """
        sql = select(self.model, AssetsCategory, AssetsLocation, AssetsDepartment)

        sql = sql.join(AssetsCategory, isouter=True)  # 左关联 AssetsCategory
        sql = sql.join(AssetsLocation, isouter=True)  # 左关联 AssetsLocation
        sql = sql.join(AssetsDepartment, isouter=True)  # 左关联 AssetsDepartment
        sql = self._make_search(sql, search.search, filter_type)
        logger.debug(sql)

        # subquery查询找到order_col的起始值
        subquery = select(getattr(self.model, order_col))
        subquery = subquery.join(
            AssetsCategory, isouter=True)  # 左关联 AssetsCategory
        subquery = subquery.join(AssetsLocation, isouter=True)
        subquery = subquery.join(AssetsDepartment, isouter=True)  # 左关联 AssetsDepartment
        subquery = self._make_search(subquery, search.search, filter_type)
        sql, subquery = self._make_pagination(sql, subquery, search, order_col)
        logger.debug(sql)

        results = session.exec(sql).all()
        return results

    def search_all(self, session: Session, search_obj: BaseModel, filter_type: Optional[Dict[str, str]] = None,
                   order_col: Optional[str] = 'updated_at'):
        """
        获取所有符合条件的资产（不分页）
        :param session:
        :param search_obj: 搜索条件对象
        :param filter_type: 指定的各属性值判断形式
        :param order_col: order排序列名
        :return:
        """
        sql = select(self.model, AssetsCategory, AssetsLocation)
        sql = sql.join(AssetsCategory, isouter=True)  # 左关联 AssetsCategory
        sql = sql.join(AssetsLocation, isouter=True)  # 左关联 AssetsLocation
        sql = self._make_search(sql, search_obj, filter_type)
        
        # 添加排序
        if hasattr(self.model, order_col):
            sql = sql.order_by(desc(getattr(self.model, order_col)))
        
        logger.debug(sql)
        results = session.exec(sql).all()
        return results

    def get_status_counts(self, session: Session, filter_type: Optional[Dict[str, str]] = None):
        """
        获取资产各状态的总数
        :param session:
        :param filter_type: 字段过滤形式
        :return:
        """
        sql = select(getattr(self.model, 'status').label(
            'group_field'), func.count().label('count'))
        sql = sql.group_by(getattr(self.model, 'status'))
        logger.debug(str(sql))
        results = session.exec(sql).all()
        return results

    def get_with_details(self, session: Session, asset_id: int) -> Optional[tuple[Assets, AssetsCategory, AssetsLocation, AssetsDepartment]]:
        """
        通过资产ID获取资产详细信息，包含分类、位置和部门信息
        :param session:
        :param asset_id: 资产ID
        :return: (资产对象, 分类对象, 位置对象, 部门对象) 或 None
        """
        sql = select(self.model, AssetsCategory, AssetsLocation, AssetsDepartment)
        sql = sql.join(AssetsCategory, isouter=True)  # 左关联 AssetsCategory
        sql = sql.join(AssetsLocation, isouter=True)  # 左关联 AssetsLocation
        sql = sql.join(AssetsDepartment, isouter=True)  # 左关联 AssetsDepartment
        sql = sql.where(self.model.id == asset_id)
        logger.debug(str(sql))
        
        result = session.exec(sql).first()
        return result

    def search_inventory_assets_total(self, session: Session, search_obj: BaseModel, filter_type: Optional[Dict[str, str]] = None) -> int:
        """
        获取符合条件的盘点资产总数（排除报废状态的资产）
        :param session:
        :param search_obj: 搜索条件对象
        :param filter_type: 字段过滤形式
        :return: 总数
        """
        sql = select(func.count(self.model.id))
        sql = sql.join(AssetsCategory, isouter=True)  # 左关联 AssetsCategory
        sql = sql.join(AssetsLocation, isouter=True)  # 左关联 AssetsLocation
        sql = sql.join(AssetsDepartment, isouter=True)  # 左关联 AssetsDepartment
        sql = sql.where(self.model.status != 3)  # 排除报废状态的资产
        sql = self._make_search(sql, search_obj, filter_type)
        logger.debug(str(sql))
        try:
            result = session.exec(sql).one()
        except NoResultFound:
            result = 0
        return result

    def search_inventory_assets(self, session: Session, search: Pagination, filter_type: Optional[Dict[str, str]] = None) -> List[tuple[Assets, AssetsCategory, AssetsLocation, AssetsDepartment]]:
        """
        搜索盘点资产（基础查询，不包含盘点状态计算，排除报废状态的资产）
        支持分页查询，提升性能
        :param session:
        :param search: 分页搜索对象
        :param filter_type: 字段过滤形式
        :return: 资产列表
        """
        sql = select(self.model, AssetsCategory, AssetsLocation, AssetsDepartment)
        sql = sql.join(AssetsCategory, isouter=True)  # 左关联 AssetsCategory
        sql = sql.join(AssetsLocation, isouter=True)  # 左关联 AssetsLocation
        sql = sql.join(AssetsDepartment, isouter=True)  # 左关联 AssetsDepartment
        sql = sql.where(self.model.status != 3)  # 排除报废状态的资产
        sql = self._make_search(sql, search.search, filter_type)
        
        # 添加排序
        sql = sql.order_by(desc(self.model.updated_at))
        
        # 添加分页
        offset = (search.page - 1) * search.page_size
        sql = sql.offset(offset).limit(search.page_size)
        
        logger.debug(str(sql))
        results = session.exec(sql).all()
        return results


class CRUDAssetsCategory(CRUDCategory[AssetsCategory]):
    def get_by_names(self, db: Session, names: List[str]) -> List[AssetsCategory]:
        if not names:
            return []
        return db.exec(select(AssetsCategory).where(AssetsCategory.name.in_(names))).all()


class CRUDAssetsLocation(CRUDCategory[AssetsLocation]):
    def get_by_names(self, db: Session, names: List[str]) -> List[AssetsLocation]:
        if not names:
            return []
        return db.exec(select(AssetsLocation).where(AssetsLocation.name.in_(names))).all()


class CRUDAssetsDepartment(CRUDCategory[AssetsDepartment]):
    def get_by_names(self, db: Session, names: List[str]) -> List[AssetsDepartment]:
        if not names:
            return []
        return db.exec(select(AssetsDepartment).where(AssetsDepartment.name.in_(names))).all()


class CRUDAssetsLogs(CRUDBase[AssetLogs]):
    def get_asset_logs(self, db: Session, asset_id: int, start: Union[date, None] = None, end: Union[date, None] = None) -> Optional[AssetLogs]:
        """
        通过资产ID获取对应的日志
        """
        sql = select(self.model).where(self.model.asset_id == asset_id)
        if start:
            if isinstance(start, date):
                start = datetime.combine(start, datetime.min.time())
            sql = sql.where(self.model.timestamp >= start)
        if end:
            if isinstance(end, date):
                end = datetime.combine(end, datetime.max.time())
            sql = sql.where(self.model.timestamp <= end)
        logger.debug(str(sql))
        return db.exec(sql).all()

    def get_recent_logs(self, db: Session, start: Union[datetime, None] = None, end: Union[datetime, None] = None) -> Optional[AssetLogs]:
        """
        获取最近7天的日志
        """
        sql = select(self.model)
        if start:
            sql = sql.where(self.model.timestamp >= start)
        else:
            start = datetime.now() - timedelta(days=1)
            sql = sql.where(self.model.timestamp >= start)
        if end:
            sql = sql.where(self.model.timestamp <= end)
        return db.exec(sql.order_by(self.model.timestamp.desc())).all()

    def get_user_logs(self, db: Session, username: str, start: Union[date, None] = None, end: Union[date, None] = None) -> Optional[AssetLogs]:
        """
        通过用户名查询资产领用和退回记录
        """
        # 构建查询条件：details字段中包含owner或previous_owner为指定用户名的记录
        # 注意：details字段是JSON字符串，需要使用JSON函数进行查询
        sql = select(self.model).where(
            and_(
                # 查询资产领用记录，details中owner字段为指定用户名
                self.model.details.like(f'%owner": "{username}"%'),
                # 只查询资产领用或资产退回的记录
                or_(
                    self.model.action == "资产领用",
                    self.model.action == "资产退回"
                )
            )
        )

        # 添加时间范围过滤
        if start:
            # 将date转换为datetime，设置为当天的开始时间
            start_datetime = datetime.combine(start, datetime.min.time())
            sql = sql.where(self.model.timestamp >= start_datetime)
        if end:
            # 将date转换为datetime，设置为当天的结束时间
            end_datetime = datetime.combine(end, datetime.max.time())
            sql = sql.where(self.model.timestamp <= end_datetime)
        logger.debug(str(sql))
        # 按时间倒序排序
        return db.exec(sql.order_by(self.model.timestamp.desc())).all()

    def search_logs(self, db: Session, search: Pagination, filter_type: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        搜索资产操作日志，支持多种过滤条件和分页
        使用基类的通用搜索和分页功能
        """
        from app.models.assets import AssetLogsWithAssetInfo
        
        # 使用基类的search_total方法计算总数
        total = self.search_logs_total(db, search.search, filter_type)
        
        # 构建联表查询，获取资产详细信息
        sql = select(
            self.model.id,
            self.model.asset_id,
            self.model.operator,
            self.model.action,
            self.model.details,
            self.model.images,
            self.model.timestamp,
            Assets.asset_code,
            Assets.name.label('asset_name'),
            AssetsCategory.name.label('category_name'),
            AssetsLocation.name.label('location_name'),
            AssetsDepartment.name.label('department_name')
        ).select_from(
            self.model.join(Assets, self.model.asset_id == Assets.id)
            .outerjoin(AssetsCategory, Assets.category_id == AssetsCategory.id)
            .outerjoin(AssetsLocation, Assets.location_id == AssetsLocation.id)
            .outerjoin(AssetsDepartment, Assets.department_id == AssetsDepartment.id)
        )

        # 使用基类的_make_search方法应用搜索条件
        sql = self._make_search(sql, search.search, filter_type)
        
        # 确定排序字段，默认按时间倒序
        order_col = search.order_by if search.order_by else 'timestamp'
        
        # 对于联表查询，需要特殊处理分页
        # 由于基类的_make_pagination方法是为单表设计的，这里仍使用手动分页
        # 但可以统一排序逻辑
        if hasattr(self.model, order_col):
            order_field = getattr(self.model, order_col)
        elif order_col == 'asset_code':
            order_field = Assets.asset_code
        elif order_col == 'asset_name':
            order_field = Assets.name
        else:
            order_field = self.model.timestamp
            
        if search.order_type == 'asc':
            sql = sql.order_by(order_field.asc())
        else:
            sql = sql.order_by(order_field.desc())

        # 应用分页 - 联表查询使用简单的offset/limit分页
        sql = sql.offset(search.offset).limit(search.limit)
        
        # 执行查询
        results = db.exec(sql).all()
        
        # 转换为模型对象
        logs_data = []
        for row in results:
            log_data = AssetLogsWithAssetInfo(
                id=row.id,
                asset_id=row.asset_id,
                operator=row.operator,
                action=row.action,
                details=row.details,
                images=row.images,
                timestamp=row.timestamp,
                asset_code=row.asset_code,
                asset_name=row.asset_name,
                category_name=row.category_name,
                location_name=row.location_name,
                department_name=row.department_name
            )
            logs_data.append(log_data)

        return {
            'total': total,
            'data': logs_data
        }

    def search_logs_total(self, session: Session, q: BaseModel = None, filter_type: Optional[Dict[str, str]] = None) -> int:
        """
        获取符合搜索条件的资产日志总数
        使用基类的通用搜索功能
        """
        # 构建联表查询的总数统计
        sql = select(func.count(self.model.id)).select_from(
            self.model.join(Assets, self.model.asset_id == Assets.id)
            .outerjoin(AssetsCategory, Assets.category_id == AssetsCategory.id)
            .outerjoin(AssetsLocation, Assets.location_id == AssetsLocation.id)
            .outerjoin(AssetsDepartment, Assets.department_id == AssetsDepartment.id)
        )
        
        # 使用基类的_make_search方法应用搜索条件
        sql = self._make_search(sql, q, filter_type)
        
        try:
            result = session.exec(sql).one()
        except NoResultFound:
            result = 0
        return result

    def _make_search(self, sql, search_params=None, filter_type=None):
        """
        构建资产日志搜索条件
        利用基类的通用搜索功能并添加特殊的联表查询条件
        """
        if search_params is None:
            return sql

        # 首先使用基类的通用搜索功能处理基本字段
        if filter_type:
            sql = super()._make_search(sql, search_params, filter_type)

        # 处理搜索参数
        if hasattr(search_params, 'model_dump'):
            q = search_params.model_dump()
        else:
            q = search_params if isinstance(search_params, dict) else {}

        # 处理特殊的联表查询条件（资产相关字段）
        # 资产编号搜索
        if q.get('asset_code'):
            sql = sql.where(Assets.asset_code.like(f"%{q['asset_code']}%"))

        # 资产名称搜索
        if q.get('asset_name'):
            sql = sql.where(Assets.name.like(f"%{q['asset_name']}%"))

        # 分类名称搜索
        if q.get('category_name'):
            sql = sql.where(AssetsCategory.name.like(f"%{q['category_name']}%"))

        # 位置名称搜索
        if q.get('location_name'):
            sql = sql.where(AssetsLocation.name.like(f"%{q['location_name']}%"))

        # 部门名称搜索
        if q.get('department_name'):
            sql = sql.where(AssetsDepartment.name.like(f"%{q['department_name']}%"))

        # 处理时间范围搜索（特殊处理，因为基类可能不支持时间范围）
        if q.get('start_time'):
            sql = sql.where(self.model.timestamp >= q['start_time'])

        if q.get('end_time'):
            sql = sql.where(self.model.timestamp <= q['end_time'])

        return sql




class CRUDInventoryBatches(CRUDBase[InventoryBatches]):
    """盘点批次CRUD操作"""

    def delete(self, db: Session, batch_id: str):
        """
        删除盘点批次
        :param db: 数据库会话
        :param batch_id: 批次ID
        :return: 删除的对象
        """
        return super().delete(db, batch_id, id_field='batch_id')

    def create_with_validation(self, session: Session, obj_in: InventoryBatches) -> tuple[bool, str, Optional[InventoryBatches]]:
        """
        创建盘点批次，包含业务逻辑验证
        返回: (是否成功, 消息, 批次对象)
        """
        try:
            # 检查是否存在active状态的盘点批次
            active_batches_stmt = select(InventoryBatches).where(
                InventoryBatches.status == "active"
            )
            active_batches = session.exec(active_batches_stmt).all()

            # 如果存在active状态的批次，则不允许创建新批次
            if active_batches:
                active_batch_names = [
                    batch.batch_name for batch in active_batches]
                error_msg = f"无法创建新的盘点批次，当前存在进行中的盘点批次：{', '.join(active_batch_names)}。请先完成或取消现有批次。"
                return False, error_msg, None

            # 创建新的盘点批次
            batch = self.insert(session, obj_in)
            return True, "盘点批次创建成功", batch

        except Exception as e:
            session.rollback()
            return False, f"创建盘点批次失败: {str(e)}", None

    def get_active_batch(self, session: Session) -> Optional[InventoryBatches]:
        """
        获取当前活动的盘点批次
        返回: 活动批次对象或None
        """
        try:
            active_batch_stmt = select(InventoryBatches).where(
                InventoryBatches.status == "active"
            ).order_by(desc(InventoryBatches.created_at))

            return session.exec(active_batch_stmt).first()

        except Exception as e:
            return None

    def get_latest_batch(self, session: Session) -> Optional[InventoryBatches]:
        """
        获取最新的盘点批次
        返回: 最新创建的盘点批次对象或None
        """
        try:
            latest_batch_stmt = select(InventoryBatches).order_by(
                desc(InventoryBatches.created_at)
            )

            return session.exec(latest_batch_stmt).first()

        except Exception as e:
            return None

    def search_total(self, session: Session, q: BaseModel = None, filter_type: Optional[Dict[str, str]] = None) -> int:
        """
        获取符合搜索条件的盘点批次总数
        重写基类方法，使用正确的主键字段
        """
        sql = select(func.count(self.model.batch_id))
        sql = self._make_search(sql, q, filter_type)
        return session.exec(sql).one()

    def get(self, session: Session, id: int) -> Optional[InventoryBatches]:
        """
        通过主键获取盘点批次
        重写基类方法，使用正确的主键字段
        """
        return session.get(InventoryBatches, id)

    def search(self, session: Session, search: Pagination, filter_type: Optional[Dict[str, str]] = None,
               order_col: Optional[str] = 'batch_id') -> List[InventoryBatches]:
        """
        分页搜索盘点批次
        重写基类方法，使用正确的主键字段
        """
        sql = select(self.model)
        sql = self._make_search(sql, search.search, filter_type)

        # 简单的排序和分页，避免复杂的子查询
        if search.model == 'desc':
            sql = sql.order_by(desc(getattr(self.model, order_col)))
        else:
            sql = sql.order_by(getattr(self.model, order_col))

        offset = (search.page - 1) * search.page_size
        sql = sql.offset(offset).limit(search.page_size)

        return session.exec(sql).all()

    def _make_search(self, sql, search: BaseModel = None, filter_type: Optional[Dict[str, str]] = None):
        """
        构建盘点批次的搜索条件
        """
        if search is None:
            return sql

        # 使用基类的通用搜索方法
        sql = super()._make_search(sql, search, filter_type)

        return sql

    def get_by_batch_id(self, session: Session, batch_id: int) -> Optional[InventoryBatches]:
        """通过批次ID获取批次信息"""
        return session.get(InventoryBatches, batch_id)

    def get_active_batches(self, session: Session) -> List[InventoryBatches]:
        """获取所有进行中的盘点批次"""
        stmt = select(InventoryBatches).where(
            InventoryBatches.status == "active")
        return session.exec(stmt).all()

    def close_batch(self, session: Session, batch_id: int) -> Optional[InventoryBatches]:
        """关闭盘点批次（设置状态为已完成并设置结束日期）"""
        batch = self.get_by_batch_id(session, batch_id)
        if batch:
            batch.status = "completed"
            batch.end_date = date.today()
            session.add(batch)
            session.commit()
            session.refresh(batch)
        return batch

    def close_batch_to_closed(self, session: Session, batch_id: int) -> Optional[InventoryBatches]:
        """关闭盘点批次（设置状态为已关闭）"""
        batch = self.get_by_batch_id(session, batch_id)
        if batch:
            batch.status = "closed"
            session.add(batch)
            session.commit()
            session.refresh(batch)
        return batch

    def get_batch_statistics(self, session: Session, batch_id: int) -> Dict[str, Any]:
        """获取盘点批次的统计信息"""
        batch = self.get_by_batch_id(session, batch_id)
        if not batch:
            return {}

        # 获取每个资产的最新盘点记录
        # 使用窗口函数ROW_NUMBER()来获取每个资产的最新记录
        # 排除报废状态(status=3)的资产
        latest_records_subquery = select(
            InventoryRecords.record_id,
            InventoryRecords.asset_id,
            InventoryRecords.action_type,
            func.row_number().over(
                partition_by=InventoryRecords.asset_id,
                order_by=desc(InventoryRecords.scanned_at)
            ).label('rn')
        ).join(
            Assets, InventoryRecords.asset_id == Assets.id
        ).where(
            and_(
                InventoryRecords.batch_id == batch_id,
                Assets.status != 3  # 排除报废状态的资产
            )
        ).subquery()

        # 只选择每个资产的最新记录（rn=1）
        latest_records_stmt = select(
            latest_records_subquery.c.record_id,
            latest_records_subquery.c.asset_id,
            latest_records_subquery.c.action_type
        ).where(
            latest_records_subquery.c.rn == 1
        )
        
        latest_records = session.exec(latest_records_stmt).all()

        # 统计各种盘点行为的数量（基于最新记录）
        action_stats = {
            'CONFIRM_IN_PLACE': 0,
            'INFO_UPDATE': 0,
            'EXCEPTION': 0,
            'NEW_ASSET': 0
        }
        
        for record in latest_records:
            if record.action_type in action_stats:
                action_stats[record.action_type] += 1

        # 涉及的资产数量（去重）
        unique_assets_scanned = len(latest_records)
        
        # 获取所有非报废状态的资产总数
        total_assets_stmt = select(func.count(Assets.id)).where(Assets.status != 3)
        total_assets = session.exec(total_assets_stmt).one()
        
        # 计算未盘点的资产数量
        unscanned_assets = total_assets - unique_assets_scanned

        return {
            "batch_info": {
                "batch_id": batch.batch_id,
                "batch_name": batch.batch_name,
                "status": batch.status,
                "start_date": batch.start_date,
                "end_date": batch.end_date
            },
            "statistics": {
                "scanned_assets": unique_assets_scanned,
                "unscanned_assets": unscanned_assets,
                "action_breakdown": {
                    "confirmed_in_place": action_stats.get('CONFIRM_IN_PLACE', 0),
                    "info_updated": action_stats.get('INFO_UPDATE', 0),
                    "exceptions": action_stats.get('EXCEPTION', 0),
                    "new_assets": action_stats.get('NEW_ASSET', 0)
                }
            }
        }


class CRUDInventoryRecords(CRUDBase[InventoryRecords]):
    """盘点记录CRUD操作"""

    def _make_search(self, sql, search: BaseModel = None, filter_type: Optional[Dict[str, str]] = None):
        """
        构建盘点记录的搜索条件
        """
        if search is None:
            return sql

        # 使用基类的通用搜索方法
        sql = super()._make_search(sql, search, filter_type)

        # 处理特殊的日期范围查询
        q = search.model_dump() if isinstance(search, BaseModel) else search

        if q.get('scanned_at_from'):
            sql = sql.where(InventoryRecords.scanned_at >=
                            q['scanned_at_from'])
        if q.get('scanned_at_to'):
            sql = sql.where(InventoryRecords.scanned_at <= q['scanned_at_to'])

        return sql

    def search_total(self, session: Session, search: BaseModel = None, filter_type: Optional[Dict[str, str]] = None) -> int:
        """
        获取符合搜索条件的盘点记录总数
        """
        sql = select(func.count(self.model.record_id))
        sql = self._make_search(sql, search, filter_type)
        return session.exec(sql).one()

    def search(self, session: Session, search: Pagination, filter_type: Optional[Dict[str, str]] = None,
               order_col: Optional[str] = 'scanned_at') -> List[InventoryRecords]:
        """
        分页搜索盘点记录
        """
        sql = select(self.model)
        sql = self._make_search(sql, search.search, filter_type)
        sql = self._make_pagination(sql, search, order_col)
        return session.exec(sql).all()

    def search_with_details(self, session: Session, search: Pagination, filter_type: Optional[Dict[str, str]] = None) -> List[InventoryRecordWithDetails]:
        """
        分页搜索带详细信息的盘点记录
        """
        # 构建联表查询
        sql = select(
            InventoryRecords.record_id,
            InventoryRecords.asset_id,
            InventoryRecords.batch_id,
            InventoryRecords.scanned_by_user_id,
            InventoryRecords.scanned_at,
            InventoryRecords.action_type,
            InventoryRecords.actual_location_id,
            InventoryRecords.actual_user,
            InventoryRecords.photo_urls,
            InventoryRecords.details,
            Assets.name.label('asset_name'),
            Assets.asset_code,
            InventoryBatches.batch_name,
            AssetsLocation.name.label('actual_location_name')
        ).select_from(
            InventoryRecords
        ).join(
            Assets, InventoryRecords.asset_id == Assets.id, isouter=True
        ).join(
            InventoryBatches, InventoryRecords.batch_id == InventoryBatches.batch_id, isouter=True
        ).join(
            AssetsLocation, InventoryRecords.actual_location_id == AssetsLocation.id, isouter=True
        )

        # 应用搜索条件
        sql = self._make_search(sql, search.search, filter_type)

        # 排序和分页
        sql = sql.order_by(desc(InventoryRecords.scanned_at))
        offset = (search.page - 1) * search.size
        sql = sql.offset(offset).limit(search.size)

        # 执行查询
        result = session.exec(sql).all()

        # 转换为响应模型
        records = []
        for row in result:
            record = InventoryRecordWithDetails(
                record_id=row.record_id,
                asset_id=row.asset_id,
                batch_id=row.batch_id,
                scanned_by_user_id=row.scanned_by_user_id,
                scanned_at=row.scanned_at,
                action_type=row.action_type,
                actual_location_id=row.actual_location_id,
                actual_user=row.actual_user,
                photo_urls=row.photo_urls,
                details=row.details,
                asset_name=row.asset_name,
                asset_code=row.asset_code,
                batch_name=row.batch_name,
                actual_location_name=row.actual_location_name,
                scanned_by_user_name=row.scanned_by_user_name
            )
            records.append(record)

        return records

    def get_by_record_id(self, session: Session, record_id: int) -> Optional[InventoryRecords]:
        """通过记录ID获取盘点记录"""
        return session.get(InventoryRecords, record_id)

    def get_records_by_batch(self, session: Session, batch_id: int, skip: int = 0, limit: int = 100) -> List[InventoryRecords]:
        """获取指定批次的盘点记录"""
        stmt = select(InventoryRecords).where(
            InventoryRecords.batch_id == batch_id).offset(skip).limit(limit)
        return session.exec(stmt).all()

    def get_records_by_asset(self, session: Session, asset_id: int) -> List[InventoryRecords]:
        """获取指定资产的所有盘点记录"""
        stmt = select(InventoryRecords).where(InventoryRecords.asset_id ==
                                              asset_id).order_by(desc(InventoryRecords.scanned_at))
        return session.exec(stmt).all()

    def get_records_with_details(self, session: Session, conditions: List = None, skip: int = 0, limit: int = 100) -> List[InventoryRecordWithDetails]:
        """获取带详细信息的盘点记录"""
        from ..models.internal import User
        
        # 构建联表查询
        stmt = select(
            InventoryRecords.record_id,
            InventoryRecords.asset_id,
            InventoryRecords.batch_id,
            InventoryRecords.scanned_by_user_id,
            InventoryRecords.scanned_at,
            InventoryRecords.action_type,
            InventoryRecords.actual_location_id,
            InventoryRecords.actual_user,
            InventoryRecords.photo_urls,
            InventoryRecords.details,
            Assets.name.label('asset_name'),
            Assets.asset_code,
            InventoryBatches.batch_name,
            AssetsLocation.name.label('actual_location_name'),
            User.name.label('scanned_by_user_name')
        ).select_from(
            InventoryRecords
        ).join(
            Assets, InventoryRecords.asset_id == Assets.id, isouter=True
        ).join(
            InventoryBatches, InventoryRecords.batch_id == InventoryBatches.batch_id, isouter=True
        ).join(
            AssetsLocation, InventoryRecords.actual_location_id == AssetsLocation.id, isouter=True
        ).join(
            User, InventoryRecords.scanned_by_user_id == User.id, isouter=True
        )

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # 排序
        stmt = stmt.order_by(desc(InventoryRecords.scanned_at))

        # 分页
        stmt = stmt.offset(skip).limit(limit)

        # 执行查询
        result = session.exec(stmt).all()

        # 转换为响应模型
        records = []
        for row in result:
            record = InventoryRecordWithDetails(
                record_id=row.record_id,
                asset_id=row.asset_id,
                batch_id=row.batch_id,
                scanned_by_user_id=row.scanned_by_user_id,
                scanned_at=row.scanned_at,
                action_type=row.action_type,
                actual_location_id=row.actual_location_id,
                actual_user=row.actual_user,
                photo_urls=row.photo_urls,
                details=row.details,
                asset_name=row.asset_name,
                asset_code=row.asset_code,
                batch_name=row.batch_name,
                actual_location_name=row.actual_location_name,
                scanned_by_user_name=row.scanned_by_user_name
            )
            records.append(record)

        return records

    def count_records(self, session: Session, conditions: List = None) -> int:
        """计算符合条件的记录数量"""
        stmt = select(func.count(InventoryRecords.record_id))
        if conditions:
            stmt = stmt.where(and_(*conditions))
        return session.exec(stmt).one()

    def get_inventory_logs_without_pagination(self, session: Session, search: BaseModel, filter_type: Optional[Dict[str, str]] = None) -> List[InventoryRecordWithDetails]:
        """
        获取资产盘点日志记录（不使用分页）
        """
        from ..models.internal import User
        
        # 构建联表查询
        sql = select(
            InventoryRecords.record_id,
            InventoryRecords.asset_id,
            InventoryRecords.batch_id,
            InventoryRecords.scanned_by_user_id,
            InventoryRecords.scanned_at,
            InventoryRecords.action_type,
            InventoryRecords.actual_location_id,
            InventoryRecords.actual_user,
            InventoryRecords.photo_urls,
            InventoryRecords.details,
            Assets.name.label('asset_name'),
            Assets.asset_code,
            InventoryBatches.batch_name,
            AssetsLocation.name.label('actual_location_name'),
            User.name.label('scanned_by_user_name')
        ).select_from(
            InventoryRecords
        ).join(
            Assets, InventoryRecords.asset_id == Assets.id, isouter=True
        ).join(
            InventoryBatches, InventoryRecords.batch_id == InventoryBatches.batch_id, isouter=True
        ).join(
            AssetsLocation, InventoryRecords.actual_location_id == AssetsLocation.id, isouter=True
        ).join(
            User, InventoryRecords.scanned_by_user_id == User.id, isouter=True
        )

        # 应用搜索条件
        sql = self._make_search(sql, search, filter_type)

        # 排序（按扫描时间倒序）
        sql = sql.order_by(desc(InventoryRecords.scanned_at))

        # 执行查询（不使用分页）
        result = session.exec(sql).all()

        # 转换为响应模型
        records = []
        for row in result:
            record = InventoryRecordWithDetails(
                record_id=row.record_id,
                asset_id=row.asset_id,
                batch_id=row.batch_id,
                scanned_by_user_id=row.scanned_by_user_id,
                scanned_at=row.scanned_at,
                action_type=row.action_type,
                actual_location_id=row.actual_location_id,
                actual_user=row.actual_user,
                photo_urls=row.photo_urls,
                details=row.details,
                asset_name=row.asset_name,
                asset_code=row.asset_code,
                batch_name=row.batch_name,
                actual_location_name=row.actual_location_name,
                scanned_by_user_name=row.scanned_by_user_name
            )
            records.append(record)

        return records

    def check_asset_inventory_status(self, session: Session, asset_id: int, batch_id: int) -> bool:
        """检查指定资产在特定批次中是否已经盘点过"""
        stmt = select(func.count(InventoryRecords.record_id)).where(
            and_(
                InventoryRecords.asset_id == asset_id,
                InventoryRecords.batch_id == batch_id
            )
        )
        count = session.exec(stmt).one()
        return count > 0


# 实例化CRUD对象
assets = CRUDAssets(Assets)
assets_category = CRUDAssetsCategory(AssetsCategory)
assets_location = CRUDAssetsLocation(AssetsLocation)
assets_department = CRUDAssetsDepartment(AssetsDepartment)
assets_logs = CRUDAssetsLogs(AssetLogs)
inventory_batches = CRUDInventoryBatches(InventoryBatches)
inventory_records = CRUDInventoryRecords(InventoryRecords)
