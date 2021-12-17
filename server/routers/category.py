from typing import Optional
import sqlalchemy.exc
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..dependencies import get_session, check_token, check_roles,check_permission
from ..sql.models import Category, CategoryField, Role
from typing import List
from pydantic import BaseModel
from ..sql.schemas import ApiResponse
from ..common import utils

router = APIRouter(prefix='/api', dependencies=[Depends(check_permission), ])


class UpdateCategory(BaseModel):
    category: Category
    fields: List[CategoryField]


@router.get('/categories/{id}/fields', description='获取对应资产的定义字段')
async def get_asset_fields(id: int, session: Session = Depends(get_session)):
    fields = session.exec(select(CategoryField).where(CategoryField.category_id == id)).all()
    info_fields = []
    for field in fields:
        info_fields.append({'label': field.desc, 'value': field.name})
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
    category: Category = session.exec(select(Category).where(Category.id == id)).one()
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
async def get_category_list(search: Optional[str] = None, session: Session = Depends(get_session),
                            roles: List[str] = Depends(check_roles)):
    role_list = session.exec(select(Role).where(Role.id.in_(roles))).all()
    role_category = []
    for role in role_list:
        role_category.extend([category.id for category in role.category])
    role_category = set(role_category)
    print('role category')
    print(role_category)
    sql = select(Category).where(Category.id.in_(role_category))
    if search is not None:
        sql = sql.where(Category.name.like('%' + search + '%'))
    categories: List[Category] = session.exec(sql).all()
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
    新建资产、更新资产信息
    :param category_info:
    :param session:
    :return:
    """
    try:
        old_category = session.exec(
            select(Category).where(Category.name == category_info.category.name)).one()
        new_category = utils.update_model(old_category, category_info.category)
    except sqlalchemy.exc.NoResultFound:
        new_category = category_info.category
    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    for field in category_info.fields:
        print(field)
        try:
            old_field = session.exec(select(CategoryField).where(CategoryField.id == field.id)).one()
            new_field = utils.update_model(old_field, field)
        except sqlalchemy.exc.NoResultFound:
            new_field = field
            new_field.category_id = new_category.id
        session.add(new_field)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )
