from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select
from ..dependencies import get_session, check_token
from pydantic import BaseModel
from ..sql import crud
from ..sql.models import Role, Menu, RoleMenu, Category, RoleCategory
from typing import List
from ..sql.schemas import ApiResponse
from ..common.utils import menu_convert

router = APIRouter(prefix='/api/role', dependencies=[Depends(check_token), ])


@router.get('/all',
            description="查询用户角色信息")
async def get_roles(session: Session = Depends(get_session)):
    roles: List[Role] = session.exec(select(Role)).all()
    return ApiResponse(
        code=0,
        message="success",
        data=roles
    )


@router.get('/menus/')
async def get_role_menus(id: Optional[int] = None, session: Session = Depends(get_session)):
    # 所有角色，进行权限分配的时候，都是返回所有菜单列表,enable=True:只查询启用的菜单
    menu_list: List[Menu] = crud.get_menu_list('admin', session, enable=True)
    user_menus = menu_convert(menu_list, 'role')
    if id is not None:
        sql = select(RoleMenu).where(RoleMenu.role_id == id)
        result = session.exec(sql)
        role_menus = [role.menu_id for role in result]
    else:
        role_menus = []
    return ApiResponse(
        code=0,
        message="success",
        data={
            "menus": user_menus,
            "enable": role_menus
        }
    )


@router.get('/category', description="角色授权页面，获取对应角色的资产信息")
async def get_role_category(id: Optional[int] = None, session: Session = Depends(get_session)):
    # 所有角色，进行权限分配的时候，都是返回所有菜单列表,enable=True:只查询启用的菜单
    category_list = session.exec(select(Category)).all()
    print(category_list)
    if id is not None:
        sql = select(RoleCategory).where(RoleCategory.role_id == id)
        result = session.exec(sql)
        role_category = [role.category_id for role in result]
    else:
        role_category = []
    return ApiResponse(
        code=0,
        message="success",
        data={
            "category": category_list,
            "enable": role_category
        }
    )


class RoleInfo(BaseModel):
    role: Role
    menus: List[int]
    category: List[int]


@router.post('/update', description="更新用户角色")
async def update_roles(role_info: RoleInfo, session: Session = Depends(get_session)):
    print(role_info)
    role_id = role_info.role.id
    if role_id is None:
        print('添加新角色')
    role_id = crud.update_role(role_info.role, session)
    crud.update_role_menus(role_id, role_info.menus, session)
    role = session.exec(select(Role).where(Role.id == role_id)).one()
    category = session.exec(select(Category).where(Category.id.in_(role_info.category))).all()
    role.category = category
    session.add(role)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )


@router.get('/del/{id}')
async def del_role(id: int, session: Session = Depends(get_session)):
    sql = select(Role).where(Role.id == id)
    role = session.exec(sql).one()
    session.delete(role)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )
