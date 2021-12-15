from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Request
from sqlmodel import Session, select
from ..dependencies import get_session, check_token
from pydantic import BaseModel
from ..sql import crud
from ..sql.models import Role, Menu, RoleMenu, Category, RoleCategory
from typing import List
from ..sql.schemas import ApiResponse
from ..common.utils import menu_convert, update_model

router = APIRouter(prefix='/api', dependencies=[Depends(check_token), ])


@router.delete('/roles/{id}')
async def del_role(id: int, session: Session = Depends(get_session)):
    sql = select(Role).where(Role.id == id)
    role = session.exec(sql).one()
    session.delete(role)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )


@router.get('/roles/enable-menus')
async def get_role_menus(id: Optional[int] = None, session: Session = Depends(get_session)):
    # 所有角色，进行权限分配的时候，都是返回所有菜单列表,enable=True:只查询启用的菜单
    menu_list: List[Menu] = crud.get_menu_list(session, enable=True)
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


@router.get('/roles/categories', description="角色授权页面，获取对应角色的资产信息")
async def get_role_category(request: Request, id: Optional[int] = None, session: Session = Depends(get_session)):
    # 所有角色，进行权限分配的时候，都是返回所有菜单列表,enable=True:只查询启用的菜单
    print(request)
    print(request.method)
    print(request.url.path)
    print(request.path_params)
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


@router.get('/roles',
            description="查询用户角色信息")
async def get_roles(q: Optional[str] = None, session: Session = Depends(get_session)):
    sql = select(Role)
    if q is not None:
        sql = sql.where(Role.name.like(f'%{q}%'))
    roles: List[Role] = session.exec(sql).all()
    return ApiResponse(
        code=0,
        message="success",
        data=roles
    )


class RoleInfo(BaseModel):
    role: Role
    menus: List[int]
    category: List[int]


@router.post('/roles', description="新建用户角色")
async def add_roles(role_info: RoleInfo, session: Session = Depends(get_session)):
    print(role_info)
    role = role_info.role
    session.add(role)
    session.commit()
    session.refresh(role)
    crud.update_role_menus(role.id, role_info.menus, session)
    category = session.exec(select(Category).where(Category.id.in_(role_info.category))).all()
    role.category = category
    session.add(role)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )


@router.put('/roles', description="更新用户角色")
async def update_roles(role_info: RoleInfo, session: Session = Depends(get_session)):
    print(role_info)

    sql = select(Role).where(Role.id == role_info.role.id)
    role = session.exec(sql).one()
    role = update_model(role, role_info.role)
    session.add(role)
    session.commit()
    session.refresh(role)
    crud.update_role_menus(role.id, role_info.menus, session)
    role = session.exec(select(Role).where(Role.id == role.id)).one()
    category = session.exec(select(Category).where(Category.id.in_(role_info.category))).all()
    role.category = category
    session.add(role)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )
