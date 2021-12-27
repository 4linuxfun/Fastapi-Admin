import copy
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..dependencies import get_session, check_permission, casbin_enforcer
from ..sql.models import Menu
from ..common import utils
from ..sql.schemas import ApiResponse

router = APIRouter(prefix='/api', dependencies=[Depends(check_permission), ])


class MenuApis(BaseModel):
    menu: Menu
    apis: List[str]


@router.get('/menus', description="查询菜单")
async def get_all_menu(q: Optional[str] = None, session: Session = Depends(get_session)):
    # 复用crud.get_menu_list,默认role为admin就是返回所有的菜单列表
    sql = select(Menu)
    if q is not None:
        sql = sql.where(Menu.name.like(f'%{q}%'))
    menu_list: List[Menu] = session.exec(sql).all()
    user_menus = utils.menu_convert(menu_list, "all")

    print(user_menus)
    return ApiResponse(
        code=0,
        message="success",
        data=user_menus
    )


@router.post('/menus', description="新建菜单")
async def add_menu(menu: Menu, session: Session = Depends(get_session)):
    """
    # 新建的菜单，还是没有授权给角色的，所以直接新增就行了
    :param menu:
    :param session:
    :return:
    """
    session.add(menu)
    session.commit()
    return ApiResponse(
        code=0,
        message="success"
    )


@router.put('/menus', description="更新菜单")
async def update_menu(menu: Menu, session: Session = Depends(get_session)):
    """
    更新菜单，涉及到原菜单对应api的更新，则需要更新对应信息
    :param menu:
    :param session:
    :return:
    """
    sql = select(Menu).where(Menu.id == menu.id)
    result = session.exec(sql).one()
    original_roles = [role.id for role in result.roles]
    original_api = copy.deepcopy(result.api)
    print(result)
    print(original_api)
    # 权限更新原则：统一删除原来的，然后统一增加新的
    if original_api != menu.api:
        print('api更新')
        print(f'original_roles:{original_roles}')
        if original_api:
            for api in original_api.split(','):
                method, path = api.split(':')
                for role in original_roles:
                    print('检查')
                    casbin_enforcer.delete_permissions_for_user(f'role_{role}')
        for api in menu.api.split(','):
            method, path = api.split(':')
            for role in original_roles:
                print(f'更新:role_{role},{path},{method}')
                casbin_enforcer.add_permission_for_user(f'role_{role}', path, method, 'allow')
            # menu_data = menu.dict(exclude_unset=True)
            # for key, value in menu_data.items():
            #     setattr(result, key, value)
    menu = utils.update_model(result, menu)
    # apis = session.exec(select(Api).where(Api.name.in_(menu_info.apis))).all()
    # menu.apis = apis
    session.add(menu)
    session.commit()
    return ApiResponse(
        code=0,
        message="success"
    )


@router.delete('/menus/{id}')
async def del_menu(id: int, session: Session = Depends(get_session)):
    sql = select(Menu).where(Menu.id == id)
    result = session.exec(sql).one()
    if result.api is not None:
        apis: List[str] = result.api.split(',')
        roles: List[int] = [role.id for role in result.roles]
        if apis and roles:
            for api in apis:
                method, path = api.split(':')
                for role in roles:
                    casbin_enforcer.delete_permission_for_user(f'role_{role}', path, method, 'allow')
    session.delete(result)
    session.commit()
    return ApiResponse(
        code=0,
        message="success"
    )
