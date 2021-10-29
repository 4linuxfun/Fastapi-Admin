from typing import List
from fastapi import APIRouter, Depends, Form
from sqlmodel import Session
from ..dependencies import get_session, check_token
from ..sql.models import Menu
from ..sql import crud
from ..common.utils import menu_convert
from ..sql.schemas import ApiResponse

router = APIRouter(prefix='/api/menu', dependencies=[Depends(check_token), ])


@router.get('/all')
async def get_all_menu(session: Session = Depends(get_session)):
    # 复用crud.get_menu_list,默认role为admin就是返回所有的菜单列表
    menu_list: List[Menu] = crud.get_menu_list('admin', session)
    user_menus = menu_convert(menu_list)

    print(user_menus)
    return ApiResponse(
        code=0,
        message="success",
        data=user_menus
    )


@router.post('/update')
async def update_menu(menuInfo: Menu, session: Session = Depends(get_session)):
    """
    菜单的id是不可变的
    更新：从id开始选择对应的menu信息，然后更新
    添加：无id字段，则表示为新添加的菜单
    :param menuInfo:
    :param session:
    :return:
    """
    print(menuInfo)
    crud.update_menu(menuInfo, session)


@router.get('/del/{id}')
async def del_menu(id, session: Session = Depends(get_session)):
    print(f'delete menu id:{id}')
    crud.delete_menu(id, session)
