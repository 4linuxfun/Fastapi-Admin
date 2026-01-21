from sqlmodel import SQLModel, Field, Column, Integer, String, Boolean, \
    Field, Relationship, Date, DateTime, TEXT, JSON, ForeignKey
from sqlmodel import func
from typing import List, Optional, Union
from datetime import datetime, date
from pydantic import BaseModel


class AssetsBase(SQLModel):
    id: Optional[int] = Field(sa_column=Column(
        'id', Integer, primary_key=True, autoincrement=True))
    name: Union[str, None] = Field(sa_column=Column(
        String(20), nullable=False, comment='资产名称'))
    asset_code: Union[str, None] = Field(
        sa_column=Column(String(100), unique=True, comment='资产编号'))
    category_id: Union[int, None] = Field(
        default=None, sa_column=Column(Integer, ForeignKey('asset_categories.id'), comment='资产分类ID'))
    model: Union[str, None] = Field(
        sa_column=Column(String(100), comment='设备型号'))
    brand: Union[str, None] = Field(
        sa_column=Column(String(100), comment='品牌'))
    serial_number: Union[str, None] = Field(
        sa_column=Column(String(100), comment='序列号'))
    financial_code: Union[str, None] = Field(
        sa_column=Column(String(50), comment='财务编码'))
    purchase_date: Union[date, None] = Field(
        sa_column=Column(Date, comment='购买日期'))
    purchase_price: Union[str, None] = Field(
        sa_column=Column(String(100), comment='购买价格'))
    location_id: Union[int, None] = Field(
        default=None, sa_column=Column(Integer, ForeignKey('asset_location.id'), comment='资产位置ID'))
    department_id: Union[int, None] = Field(
        default=None, sa_column=Column(Integer, ForeignKey('asset_departments.id'), comment='使用部门ID'))
    owner: Union[str, None] = Field(
        sa_column=Column(String(100), comment='使用人'))
    status: Union[str, None] = Field(sa_column=Column(
        String(50), comment='资产状态:0-在库,1-使用中,2-维修中,3-报废,4-其他'))
    specifications: Union[str, None] = Field(
        sa_column=Column(String(100), comment='规格'))
    remarks: Union[str, None] = Field(
        sa_column=Column(String(100), comment='备注'))
    last_inventory_batch_id: Union[int, None] = Field(
        default=None, sa_column=Column(
            Integer, ForeignKey('inventory_batches.batch_id'), comment='最近盘点批次ID'))
    last_inventory_time: Union[datetime, None] = Field(sa_column=Column(
        DateTime, comment='最近盘点时间'))
    created_at: Union[datetime, None] = Field(sa_column=Column(
        DateTime, comment='创建时间'))
    updated_at: Union[datetime, None] = Field(
        sa_column=Column(DateTime, comment='更新时间'))
    image_urls: Union[List[str], None] = Field(
        sa_column=Column(JSON, comment='资产图片URL列表'))


class Assets(AssetsBase, table=True):
    # 资产
    __tablename__ = 'assets'

    category: Optional["AssetsCategory"] = Relationship(
        back_populates="assets")
    location: Optional["AssetsLocation"] = Relationship(
        back_populates="assets")
    department: Optional["AssetsDepartment"] = Relationship(
        back_populates="assets")
    logs: List["AssetLogs"] = Relationship(back_populates="asset")
    last_inventory_batch: Optional["InventoryBatches"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Assets.last_inventory_batch_id]"})
    inventory_records: List["InventoryRecords"] = Relationship(
        back_populates="asset")


class AssetsCategory(SQLModel, table=True):
    # 资产分类表
    __tablename__ = 'asset_categories'
    id: Optional[int] = Field(sa_column=Column(
        'id', Integer, primary_key=True, autoincrement=True))
    name: Union[str, None] = Field(sa_column=Column(
        String(100), nullable=False, comment='资产分类名称'))
    code: Union[str, None] = Field(sa_column=Column(
        String(100), unique=True, comment='分类编码'))
    parent_id: Optional[int] = Field(
        sa_column=Column(Integer, default=None, comment='父级ID'))
    assets: List["Assets"] = Relationship(back_populates="category")


class AssetsLocation(SQLModel, table=True):
    # 资产存放位置表
    __tablename__ = 'asset_location'
    id: Optional[int] = Field(sa_column=Column(
        'id', Integer, primary_key=True, autoincrement=True))
    name: Union[str, None] = Field(sa_column=Column(
        String(100), nullable=False, comment='资产存放位置'))
    code: Union[str, None] = Field(sa_column=Column(
        String(100), unique=True, comment='位置编码'))
    parent_id: Optional[int] = Field(
        sa_column=Column(Integer, default=None, comment='父级ID'))
    assets: List["Assets"] = Relationship(back_populates="location")


class AssetsDepartment(SQLModel, table=True):
    # 资产部门表
    __tablename__ = 'asset_departments'
    id: Optional[int] = Field(sa_column=Column(
        'id', Integer, primary_key=True, autoincrement=True))
    name: Union[str, None] = Field(sa_column=Column(
        String(100), nullable=False, comment='部门名称'))
    code: Union[str, None] = Field(sa_column=Column(
        String(100), unique=True, comment='部门编码'))
    parent_id: Optional[int] = Field(
        sa_column=Column(Integer, default=None, comment='父级ID'))
    assets: List["Assets"] = Relationship(back_populates="department")


class AssetsStatus(SQLModel, table=True):
    # 资产状态表
    __tablename__ = 'asset_status'
    id: Optional[int] = Field(sa_column=Column(
        'id', Integer, primary_key=True, autoincrement=True))
    name: Union[str, None] = Field(sa_column=Column(
        String(100), nullable=False, comment='资产状态名称'))
    code: Union[str, None] = Field(sa_column=Column(
        String(50), nullable=False, unique=True, comment='资产状态编码'))


class AssetsCategoryWithChild(SQLModel):
    # 资产分类树形结构
    id: Union[int, None]
    name: Union[str, None]
    code: Union[str, None]
    parent_id: Union[int, None]
    children: List['AssetsCategoryWithChild'] = []


class AssetsLocationWithChild(SQLModel):
    # 资产位置树形结构
    id: Union[int, None]
    name: Union[str, None]
    code: Union[str, None]
    parent_id: Union[int, None]
    children: List['AssetsLocationWithChild'] = []


class AssetsDepartmentWithChild(SQLModel):
    # 资产部门树形结构
    id: Union[int, None]
    name: Union[str, None]
    code: Union[str, None]
    parent_id: Union[int, None]
    children: List['AssetsDepartmentWithChild'] = []


AssetsCategoryWithChild.model_rebuild()
AssetsLocationWithChild.model_rebuild()
AssetsDepartmentWithChild.model_rebuild()


class AssetWithCategory(AssetsBase):
    """
    返回带category_name字段的资产模型
    """
    category_name: Union[str, None]
    location_name: Union[str, None]
    department_name: Union[str, None]


class AssetWithInventoryStatusAndAction(AssetWithCategory):
    """
    返回带盘点状态和最新盘点行为类型的资产模型，继承自AssetWithCategory
    """
    inventory_status: int = Field(description="盘点状态：0-未盘点，1-已盘点（包含异常）")
    latest_action_type: Optional[str] = Field(
        default=None, description="最新盘点行为类型：CONFIRM_IN_PLACE在位确认, INFO_UPDATE信息更新, EXCEPTION异常, NEW_ASSET新增资产")

# 资产变更日志表


class AssetLogs(SQLModel, table=True):
    __tablename__ = 'asset_logs'
    id: Optional[int] = Field(sa_column=Column(
        'id', Integer, primary_key=True, autoincrement=True))
    asset_id: Optional[int] = Field(default=None, sa_column=Column(
        Integer, ForeignKey('assets.id'), comment='资产ID'))
    operator: Union[str, None] = Field(
        sa_column=Column(String(50), comment='操作人'))
    action: Union[str, None] = Field(
        sa_column=Column(String(100), comment='操作类型'))
    details: Union[str, None] = Field(
        sa_column=Column(TEXT, comment='变更详情'))
    images: Union[str, None] = Field(
        sa_column=Column(TEXT, comment='资产图片'))
    timestamp: Union[datetime, None] = Field(
        sa_column=Column(DateTime, comment='变更时间'))

    asset: Optional["Assets"] = Relationship(back_populates="logs")

# # 资产维护表
# class AssetMaintenance(SQLModel, table=True):
#     __tablename__ = 'asset_maintenance'
#     id: Optional[int] = Field(sa_column=Column('id', Integer, primary_key=True, autoincrement=True))
#     asset_id: Union[int, None] = Field(sa_column=Column(Integer, comment='资产ID'))
#     user_id: Union[int, None] = Field(sa_column=Column(Integer, comment='操作人ID'))
#     maintenance_date: Union[datetime, None] = Field(sa_column=Column(DateTime, comment='维护日期'))
#     maintenance_details: Union[str, None] = Field(sa_column=Column(String(100), comment='维护详情'))
#     cost: Union[str, None] = Field(sa_column=Column(String(100), comment='维护费用'))
#     next_maintenance_date: Union[date, None] = Field(sa_column=Column(Date, comment='下次维护日期'))


class AssetsSearch(SQLModel):
    name: Optional[str] = None
    asset_code: Optional[str] = None
    serial_number: Optional[str] = None
    financial_code: Optional[str] = None
    category_code: Optional[str] = None
    location_code: Optional[str] = None
    department_code: Optional[str] = None
    category_id: Union[List[int], None] = None
    location_id: Union[List[int], None] = None
    department_id: Union[List[int], None] = None
    model: Optional[str] = None
    brand: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[int] = None


class AssetLogsSearch(SQLModel):
    """资产操作日志搜索参数模型"""
    asset_id: Optional[int] = None
    asset_code: Optional[str] = None
    asset_name: Optional[str] = None
    operator: Optional[str] = None
    action: Optional[str] = None
    category_id: Optional[int] = None
    location_id: Optional[int] = None
    department_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class AssetLogsWithAssetInfo(SQLModel):
    """包含资产信息的日志数据模型"""
    id: Optional[int] = None
    asset_id: Optional[int] = None
    operator: Optional[str] = None
    action: Optional[str] = None
    details: Optional[str] = None
    images: Optional[str] = None
    timestamp: Optional[datetime] = None
    # 关联的资产信息
    asset_code: Optional[str] = None
    asset_name: Optional[str] = None
    category_name: Optional[str] = None
    location_name: Optional[str] = None
    department_name: Optional[str] = None


class InventoryAssetsSearch(SQLModel):
    """盘点资产搜索模型"""
    asset_code: Optional[str] = Field(default=None, description="资产编号")
    inventory_status: Optional[int] = Field(
        default=None, description="盘点状态：0-未盘点，1-已盘点（包含异常）")
    last_inventory_batch_id: Optional[int] = Field(
        default=None, description="最近盘点批次ID")
    action_type: Optional[str] = Field(
        default=None, description="盘点行为类型：CONFIRM_IN_PLACE在位确认, INFO_UPDATE信息更新, EXCEPTION异常, NEW_ASSET新增资产")


class AssetsEntry(AssetsBase):
    # 资产入库提交字段
    pass


class AssetsAllocation(SQLModel):
    id: int
    location_id: int
    department_id: Union[int, None] = None
    owner: str
    updated_at: Union[datetime, None] = None
    remarks: Union[str, None] = None
    status: int = 1
    image_urls: Union[List[str], None] = None


class AssetsReturn(SQLModel):
    id: int
    location_id: int
    owner: Optional[str] = None
    status: int = 0
    department_id: Optional[int] = None  # 退回时重置使用部门
    updated_at: Optional[datetime] = None
    image_urls: Union[List[str], None] = None


class AssetsDisposal(SQLModel):
    id: int
    status: int = 3
    location_id: Optional[int] = None
    remarks: Optional[str] = None
    image_urls: Union[List[str], None] = None


class AssetsTransfer(SQLModel):
    id: int
    location_id: int
    department_id: Union[int, None] = None
    owner: str
    updated_at: Union[datetime, None] = None
    remarks: Union[str, None] = None
    status: int = 1  # 转移后状态保持为已领用
    image_urls: Union[List[str], None] = None


# 盘点批次表
class InventoryBatches(SQLModel, table=True):
    __tablename__ = 'inventory_batches'

    batch_id: Optional[int] = Field(sa_column=Column(
        'batch_id', Integer, primary_key=True, autoincrement=True, comment='盘点批次ID'))
    batch_name: Union[str, None] = Field(sa_column=Column(
        String(100), nullable=False, comment='批次名称'))
    start_date: Union[date, None] = Field(sa_column=Column(
        Date, nullable=False, comment='盘点批次开始日期'))
    end_date: Union[date, None] = Field(sa_column=Column(
        Date, comment='盘点批次结束日期'))
    status: Union[str, None] = Field(sa_column=Column(
        String(20), nullable=False, default='active', comment='批次状态：active进行中、completed已完成、closed已关闭'))
    created_by_user_id: Union[int, None] = Field(sa_column=Column(
        Integer, nullable=False, comment='创建该批次的用户ID'))
    created_at: Union[datetime, None] = Field(sa_column=Column(
        DateTime, nullable=False, default=datetime.now, comment='创建时间'))

    # 关联关系
    inventory_records: List["InventoryRecords"] = Relationship(
        back_populates="batch")
    assets_with_last_inventory: List["Assets"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Assets.last_inventory_batch_id]"})


# 盘点记录表
class InventoryRecords(SQLModel, table=True):
    __tablename__ = 'inventory_records'

    record_id: Optional[int] = Field(sa_column=Column(
        'record_id', Integer, primary_key=True, autoincrement=True, comment='盘点记录ID'))
    asset_id: Union[int, None] = Field(sa_column=Column(
        Integer, ForeignKey('assets.id'), nullable=True, comment='关联的资产ID'))
    batch_id: Union[int, None] = Field(sa_column=Column(
        Integer, ForeignKey('inventory_batches.batch_id'), nullable=True, comment='关联的盘点批次ID'))
    scanned_by_user_id: Union[int, None] = Field(sa_column=Column(
        Integer, nullable=False, comment='执行扫描的用户ID'))
    scanned_at: Union[datetime, None] = Field(sa_column=Column(
        DateTime, nullable=False, default=datetime.now, comment='扫描时间'))
    action_type: Union[str, None] = Field(sa_column=Column(
        String(50), nullable=False, comment='盘点行为类型：CONFIRM_IN_PLACE在位确认, INFO_UPDATE信息更新, EXCEPTION异常, NEW_ASSET新增资产'))
    actual_location_id: Union[int, None] = Field(sa_column=Column(
        Integer, ForeignKey('asset_location.id'), nullable=True, comment='扫描时资产的实际位置ID'))
    actual_user: Union[str, None] = Field(sa_column=Column(
        String(50), comment='扫描时资产的实际使用人'))
    photo_urls: Union[List[str], None] = Field(sa_column=Column(
        JSON, comment='存储照片URL数组'))
    details: Union[dict, None] = Field(sa_column=Column(
        JSON, comment='存储可变的详细信息/异常原因，如旧值/新值、损坏类型、丢失描述等'))

    # 关联关系
    asset: Optional["Assets"] = Relationship(
        back_populates="inventory_records")
    batch: Optional["InventoryBatches"] = Relationship(
        back_populates="inventory_records")
    actual_location: Optional["AssetsLocation"] = Relationship()


# 盘点批次相关的请求/响应模型
class InventoryBatchCreate(SQLModel):
    """创建盘点批次的请求模型"""
    batch_name: str = Field(description="批次名称")
    start_date: date = Field(description="盘点开始日期")
    end_date: Optional[date] = Field(default=None, description="盘点结束日期")


class InventoryBatchUpdate(SQLModel):
    """更新盘点批次的请求模型"""
    batch_name: Optional[str] = Field(default=None, description="批次名称")
    start_date: Optional[date] = Field(default=None, description="盘点开始日期")
    end_date: Optional[date] = Field(default=None, description="盘点结束日期")
    status: Optional[str] = Field(default=None, description="批次状态")


class InventoryBatchSearch(SQLModel):
    """盘点批次搜索模型"""
    batch_name: Optional[str] = Field(default=None, description="批次名称")
    status: Optional[str] = Field(default=None, description="批次状态")
    start_date: Optional[date] = Field(
        default=None, description="开始日期")
    end_date: Optional[date] = Field(
        default=None, description="结束日期")
    created_by_user_id: Optional[int] = Field(
        default=None, description="创建人ID")


# 盘点记录相关的请求/响应模型
class InventoryRecordCreate(SQLModel):
    """创建盘点记录的请求模型"""
    asset_id: int = Field(description="资产ID")
    batch_id: int = Field(description="盘点批次ID")
    action_type: str = Field(description="盘点行为类型")
    actual_location_id: Optional[int] = Field(
        default=None, description="实际位置ID")
    actual_user: Optional[str] = Field(default=None, description="实际使用人")
    photo_urls: Optional[List[str]] = Field(
        default=None, description="照片URL列表")
    details: Optional[dict] = Field(default=None, description="详细信息")


class InventoryRecordWithNewAsset(SQLModel):
    """盘点发现新资产的请求模型"""
    # 盘点记录基本信息
    batch_id: int = Field(description="盘点批次ID")
    action_type: str = Field(description="盘点行为类型，应为NEW_ASSET")
    actual_status: Optional[str] = Field(default=None, description="实际状态")
    actual_location_id: Optional[int] = Field(
        default=None, description="实际位置ID")
    actual_owner: Optional[str] = Field(default=None, description="实际使用人")
    remarks: Optional[str] = Field(default=None, description="盘点备注")

    # 新资产创建信息（必填）
    asset_name: str = Field(description="资产名称")
    category_id: int = Field(description="资产分类ID")
    location_id: int = Field(description="资产位置ID")
    serial_number: str = Field(description="序列号")
    model: str = Field(description="设备型号")
    brand: str = Field(description="品牌")

    # 新资产创建信息（可选）
    purchase_date: Optional[date] = Field(default=None, description="购买日期")
    financial_code: Optional[str] = Field(default=None, description="财务编码")
    specifications: Optional[str] = Field(default=None, description="规格")
    asset_remarks: Optional[str] = Field(default=None, description="资产备注")


class InventoryRecordSearch(SQLModel):
    """盘点记录搜索模型"""
    asset_id: Optional[int] = Field(default=None, description="资产ID")
    batch_id: Optional[int] = Field(default=None, description="盘点批次ID")
    action_type: Optional[str] = Field(default=None, description="盘点行为类型")
    scanned_by_user_id: Optional[int] = Field(
        default=None, description="扫描人ID")
    scanned_at_from: Optional[datetime] = Field(
        default=None, description="扫描时间范围-起始")
    scanned_at_to: Optional[datetime] = Field(
        default=None, description="扫描时间范围-结束")


class InventoryRecordWithDetails(SQLModel):
    """带详细信息的盘点记录响应模型"""
    record_id: Optional[int]
    asset_id: Optional[int]
    batch_id: Optional[int]
    scanned_by_user_id: Optional[int]
    scanned_at: Optional[datetime]
    action_type: Optional[str]
    actual_location_id: Optional[int]
    actual_user: Optional[str]
    photo_urls: Optional[List[str]]
    details: Optional[dict]
    # 关联信息
    asset_name: Optional[str] = Field(default=None, description="资产名称")
    asset_code: Optional[str] = Field(default=None, description="资产编号")
    batch_name: Optional[str] = Field(default=None, description="批次名称")
    actual_location_name: Optional[str] = Field(
        default=None, description="实际位置名称")
    scanned_by_user_name: Optional[str] = Field(
        default=None, description="盘点人姓名")
