from typing import Optional, List
from loguru import logger
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlmodel import Session
from sqlalchemy.exc import NoResultFound
from ...common.response_code import ApiResponse
from ...common.auth_casbin import Authority
from ...common.database import get_session
from ... import crud
from ...models.internal import Role, Menu
from ...models.internal.role import RoleBase, RoleWithMenus, RoleInsert, RoleUpdate
from server.models.internal import Pagination
from ...common.utils import menu_convert

router = APIRouter(prefix='/api')


@router.get('/roles/enable-menus', summary='获取角色菜单')
async def get_role_menus(id: Optional[int] = None, session: Session = Depends(get_session)):
    """
    返回菜单，和已分配权限菜单
    :param id:
    :param session:
    :return:
    """
    # 所有角色，进行权限分配的时候，都是返回所有菜单列表,enable=True:只查询启用的菜单
    menu_list: List[Menu] = crud.internal.role.get_all_menus(session)
    user_menus = menu_convert(menu_list)
    role_menus = crud.internal.role.get_enable_menus(session, id)
    return ApiResponse(
        data={
            "menus": user_menus,
            "enable": role_menus
        }
    )


@router.post('/roles/search',
             summary="查询角色")
async def get_roles(search: Pagination[RoleBase], session: Session = Depends(get_session)):
    total = crud.internal.role.search_total(session, search.search, {'name': 'like', 'enable': 'eq'})
    logger.debug(total)
    roles: List[Role] = crud.internal.role.search(session, search, {'name': 'like', 'enable': 'eq'})
    role_with_menus: List[RoleWithMenus] = []
    for role in roles:
        new_role = RoleWithMenus(**role.model_dump(), menus=role.menus)
        role_with_menus.append(new_role)
    return ApiResponse(
        data={
            'total': total,
            'data': role_with_menus
        }
    )


@router.get('/roles/exist', summary='角色是否存在')
async def check_uname_exist(name: str, session: Session = Depends(get_session)):
    try:
        crud.internal.role.check_exist(session, name)
    except NoResultFound:
        return ApiResponse()
    else:
        return ApiResponse(
            message='error',
            data='error'
        )


@router.post('/roles', summary="新建角色", response_model=ApiResponse[Role],
             dependencies=[Depends(Authority('role:add'))])
async def add_roles(role_info: RoleInsert, session: Session = Depends(get_session)):
    logger.debug(role_info)
    enable_menus = role_info.menus
    delattr(role_info, 'menus')
    try:
        db_obj = crud.internal.role.insert(session, Role(**role_info.model_dump()))
        crud.internal.role.update_menus(session, db_obj, enable_menus)
        return ApiResponse(
            data=db_obj
        )
    except Exception as e:
        logger.error(f"add role error:{str(e)}")
        return ApiResponse(
            code=500,
            message=f"新建角色错误"
        )


@router.put('/roles', summary="更新角色", response_model=ApiResponse[Role],
            dependencies=[Depends(Authority('role:update'))])
async def update_roles(role_info: RoleUpdate, session: Session = Depends(get_session)):
    logger.debug(role_info)
    if role_info.name == 'admin':
        ApiResponse(code=status.HTTP_400_BAD_REQUEST, message='admin权限组无法更新信息')
    db_obj = crud.internal.role.get(session, role_info.id)
    enable_menus = role_info.menus
    delattr(role_info, 'menus')
    db_obj = crud.internal.role.update(session, db_obj, role_info)
    crud.internal.role.update_menus(session, db_obj, enable_menus)
    return ApiResponse(
        data=db_obj
    )


@router.delete('/roles/{id}', summary='删除角色', dependencies=[Depends(Authority('role:del'))],
               status_code=status.HTTP_204_NO_CONTENT)
async def del_role(id: int, session: Session = Depends(get_session)):
    db_obj = crud.internal.role.get(session, id)
    if db_obj.name == 'admin':
        raise HTTPException(status_code=400, detail='admin用户组无法删除')
    if len(db_obj.users) > 0:
        raise HTTPException(status_code=400, detail='有用户关联此角色')
    crud.internal.role.delete(session, id)
