from typing import Optional, List
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlmodel import Session
from ...dependencies import check_permission
from ...db import get_session
from ... import crud
from ...models.internal import Role, Menu
from ...models.internal.role import RoleWithMenus, RoleInsert, RoleUpdate
from ...common.utils import menu_convert

router = APIRouter(prefix='/api', dependencies=[Depends(check_permission), ])


@router.get('/roles/enable-menus', summary='获取角色菜单')
async def get_role_menus(id: Optional[int] = None, session: Session = Depends(get_session)):
    """
    返回菜单，和已分配权限菜单
    :param id:
    :param session:
    :return:
    """
    # 所有角色，进行权限分配的时候，都是返回所有菜单列表,enable=True:只查询启用的菜单
    menu_list: List[Menu] = crud.role.get_all_menus(session)
    user_menus = menu_convert(menu_list)
    role_menus = crud.role.get_enable_menus(session, id)
    return {
        "menus": user_menus,
        "enable": role_menus
    }


@router.get('/roles',
            summary="查询角色")
async def get_roles(q: Optional[str] = None, session: Session = Depends(get_session)):
    total = crud.role.search_total(session, q)
    print(total)
    roles: List[Role] = crud.role.search(session, q)
    role_with_menus: List[RoleWithMenus] = []
    for role in roles:
        new_role = RoleWithMenus(**role.dict(), menus=role.menus)
        role_with_menus.append(new_role)
    return {
        'total': total,
        'data': role_with_menus
    }


@router.post('/roles', summary="新建角色")
async def add_roles(role_info: RoleInsert, session: Session = Depends(get_session)):
    print(role_info)
    enable_menus = role_info.menus
    delattr(role_info, 'menus')
    db_obj = crud.role.insert(session, Role(**role_info.dict()))
    crud.role.update_menus(session, db_obj, enable_menus)
    return db_obj


@router.put('/roles', summary="更新角色")
async def update_roles(role_info: RoleUpdate, session: Session = Depends(get_session)):
    print(role_info)
    if role_info.name == 'admin':
        raise HTTPException(status_code=403, detail='admin权限组无法更新信息')
    db_obj = crud.role.get(session, role_info.id)
    enable_menus = role_info.menus
    delattr(role_info, 'menus')
    db_obj = crud.role.update(session, db_obj, role_info)
    crud.role.update_menus(session, db_obj, enable_menus)
    return db_obj


@router.delete('/roles/{id}', summary='删除角色', status_code=status.HTTP_204_NO_CONTENT)
async def del_role(id: int, session: Session = Depends(get_session)):
    db_obj = crud.role.get(session, id)
    if db_obj.name == 'admin':
        raise HTTPException(status_code=400, detail='admin用户组无法删除')
    if len(db_obj.users) > 0:
        raise HTTPException(status_code=400, detail='有用户关联此角色')
    crud.role.delete(session, id)
