from typing import Optional
from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..dependencies import get_session
from ..models import Menu
from ..common import utils
from ..schemas import ApiResponse
from .. import crud

router = APIRouter(prefix='/api')


@router.get('/menus', description="查询菜单")
async def get_all_menu(q: Optional[str] = None, session: Session = Depends(get_session)):
    # 复用crud.get_menu_list,默认role为admin就是返回所有的菜单列表
    menu_list = crud.menu.search(session, q)
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
    crud.menu.insert(session, menu)
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
    db_obj = crud.menu.get(session, menu.id)
    crud.menu.update(session, db_obj, menu)
    return ApiResponse(
        code=0,
        message="success"
    )


@router.delete('/menus/{id}')
async def del_menu(id: int, session: Session = Depends(get_session)):
    crud.menu.delete(session, id)
    return ApiResponse(
        code=0,
        message="success"
    )
