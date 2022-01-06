from typing import Optional, List
import sqlalchemy.exc
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..dependencies import get_session, check_uid
from ..sql.models import Category, CategoryField, User
from ..schemas import ApiResponse
from ..schemas.category import UpdateCategory
from .. import crud
from ..common import utils

router = APIRouter(prefix='/api')


@router.get('/categories/{id}/fields', description='获取对应资产的定义字段')
async def get_asset_fields(id: int, session: Session = Depends(get_session)):
    fields = crud.category.get_category_fields(session, id)
    info_fields = []
    for field in fields:
        info_fields.append({'label': field.name, 'value': field.name})
    return ApiResponse(
        code=0,
        message="success",
        data=[
            {
                'label': '通用字段',
                'options': [
                    {
                        'label': '资产类别',
                        'value': 'category'
                    },
                    {
                        'label': '使用人',
                        'value': 'user'
                    },
                    {
                        'label': '管理员',
                        'value': 'manager'
                    },
                    {
                        'label': '区域',
                        'value': 'area'
                    }
                ]
            },
            {
                'label': '专用字段',
                'options': info_fields
            }
        ]
    )


@router.get('/categories/{id}/detail', description="返回资产和字段信息")
async def get_category_detail(id: int, session: Session = Depends(get_session)):
    category: Category = crud.category.get(session, id)
    print(category)
    return ApiResponse(
        code=0,
        message="success",
        data={
            'category': category,
            'fields': category.fields
        }
    )


@router.get('/categories', description="资产表实时查询当前资产列表")
async def get_category_list(search: Optional[str] = None, uid: int = Depends(check_uid),
                            session: Session = Depends(get_session)):
    user = crud.user.get(session, uid)
    role_category = []
    for role in user.roles:
        role_category.extend([category.id for category in role.category])
    role_category = set(role_category)
    print('role category')
    print(role_category)
    categories = crud.category.get_role_categories(session, role_category, search)
    print(categories)
    if not categories:
        return ApiResponse(
            code=1,
            message="error",
            data="无权限访问或无此资产"
        )
    # category_list = [cate.dict(exclude={'alias': True, 'desc': True}) for cate in categories]
    # print(category_list)
    return ApiResponse(
        code=0,
        message="success",
        data=categories
    )


@router.post('/categories', description="添加资产")
async def add_category(category_info: UpdateCategory, session: Session = Depends(get_session)):
    """
    新建资产
    :param category_info:
    :param session:
    :return:
    """
    db_obj = crud.category.insert(session, category_info.category)
    crud.category.update_fields(session, db_obj, category_info.fields)
    return ApiResponse(
        code=0,
        message="success",
    )


@router.put('/categories/{id}', description="更新资产")
async def update_category(id: int, category_info: UpdateCategory, session: Session = Depends(get_session)):
    """
    新建资产
    :param id:资产编号
    :param category_info:
    :param session:
    :return:
    """
    db_obj = crud.category.get(session, id)
    db_obj = crud.category.update(session, db_obj, category_info.category)
    crud.category.update_fields(session, db_obj, category_info.fields)
    return ApiResponse(
        code=0,
        message="success",
    )
