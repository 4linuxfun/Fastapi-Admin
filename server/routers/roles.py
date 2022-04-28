from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..dependencies import check_permission
from ..db import get_session
from .. import crud
from ..models import Role, Menu
from ..schemas import ApiResponse
from ..schemas.role import RoleInfo
from ..common.utils import menu_convert

router = APIRouter(prefix='/api', dependencies=[Depends(check_permission), ])


@router.get('/roles/enable-menus', summary='获取角色菜单')
async def get_role_menus(id: Optional[int] = None, session: Session = Depends(get_session)):
    # 所有角色，进行权限分配的时候，都是返回所有菜单列表,enable=True:只查询启用的菜单
    menu_list: List[Menu] = crud.role.get_all_menus(session)
    user_menus = menu_convert(menu_list, 'all')
    role_menus = crud.role.get_roles_by_id(session, id)
    return ApiResponse(
        code=0,
        message="success",
        data={
            "menus": user_menus,
            "enable": role_menus
        }
    )


@router.get('/roles/categories', summary="获取角色资产")
async def get_role_category(id: Optional[int] = None, session: Session = Depends(get_session)):
    # 所有角色，进行权限分配的时候，都是返回所有菜单列表,enable=True:只查询启用的菜单
    category_list = crud.category.get_all_catagories(session)
    print(category_list)
    role_category = crud.category.get_categories_by_roles(session, id)
    return ApiResponse(
        code=0,
        message="success",
        data={
            "category": category_list,
            "enable": role_category
        }
    )


@router.get('/roles',
            summary="查询角色")
async def get_roles(q: Optional[str] = None, session: Session = Depends(get_session)):
    total = crud.role.search_total(session, q)
    print(total)
    roles: List[Role] = crud.role.search(session, q)
    return {
        'total': total,
        'data': roles
    }


@router.post('/roles', summary="新建角色")
async def add_roles(role_info: RoleInfo, session: Session = Depends(get_session)):
    print(role_info)
    db_obj = crud.role.insert(session, role_info.role)
    crud.role.update_menus(session, db_obj, role_info.menus)
    crud.role.update_categories(session, db_obj, role_info.category)
    return ApiResponse(
        code=0,
        message="success",
    )


@router.put('/roles', summary="更新角色")
async def update_roles(role_info: RoleInfo, session: Session = Depends(get_session)):
    print(role_info)
    if role_info.role.name == 'admin':
        return ApiResponse(
            code=1,
            message="error",
            data="admin权限组无法更新信息"
        )
    db_obj = crud.role.get(session, role_info.role.id)
    db_obj = crud.role.update(session, db_obj, role_info.role)
    crud.role.update_menus(session, db_obj, role_info.menus)
    crud.role.update_categories(session, db_obj, role_info.category)
    return ApiResponse(
        code=0,
        message="success",
    )


@router.delete('/roles/{id}', summary='删除角色')
async def del_role(id: int, session: Session = Depends(get_session)):
    db_obj = crud.role.get(session, id)
    if db_obj.name == 'admin':
        return ApiResponse(
            code=1,
            message="error",
            data="admin用户组无法删除"
        )
    crud.role.delete(session, id)
    return ApiResponse(
        code=0,
        message="success",
    )
