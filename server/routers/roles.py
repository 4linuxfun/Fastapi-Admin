from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from ..dependencies import get_session, check_token
from pydantic import BaseModel
from ..sql import crud
from ..sql.models import Role, Menu
from typing import List
from ..sql.schemas import ApiResponse
from ..common.utils import menu_convert

router = APIRouter(prefix='/api/role', dependencies=[Depends(check_token), ])


@router.get('/all',
            description="查询用户角色信息")
async def get_roles(session: Session = Depends(get_session)):
    roles: List[Role] = crud.get_roles(session)
    return ApiResponse(
        code=0,
        message="success",
        data=roles
    )


@router.get('/menus/')
async def get_role_menus(id: Optional[int] = None, session: Session = Depends(get_session)):
    # 所有角色，进行权限分配的时候，都是返回所有菜单列表,enable=True:只查询启用的菜单
    menu_list: List[Menu] = crud.get_menu_list('admin', session, enable=True)
    user_menus = menu_convert(menu_list)
    if id is not None:
        role_menus = crud.get_role_menus(id, session)
    else:
        role_menus = []
    print(role_menus)
    print(user_menus)
    return ApiResponse(
        code=0,
        message="success",
        data={
            "menus": user_menus,
            "enable": role_menus
        }
    )


class RoleInfo(BaseModel):
    role: Role
    menus: List[int]


@router.post('/update', description="更新用户角色")
async def update_roles(role_info: RoleInfo, session: Session = Depends(get_session)):
    print(role_info)
    role_id = role_info.role.id
    if role_id is None:
        print('添加新角色')
    role_id = crud.update_role(role_info.role, session)
    crud.update_role_menus(role_id, role_info.menus, session)
    return ApiResponse(
        code=0,
        message="success",
    )


@router.get('/del/{id}')
async def del_role(id: int, session: Session = Depends(get_session)):
    crud.delete_role(id, session)
    return ApiResponse(
        code=0,
        message="success",
    )
