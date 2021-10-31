from typing import List
from fastapi import APIRouter, Depends, Form
from sqlmodel import Session, select
from ..dependencies import get_session, check_token
from ..sql.models import Menu
from ..sql import crud
from ..common import utils
from ..sql.schemas import ApiResponse

router = APIRouter(prefix='/api/menu', dependencies=[Depends(check_token), ])


@router.get('/all')
async def get_all_menu(session: Session = Depends(get_session)):
    # 复用crud.get_menu_list,默认role为admin就是返回所有的菜单列表
    menu_list: List[Menu] = crud.get_menu_list('admin', session)
    user_menus = utils.menu_convert(menu_list)

    print(user_menus)
    return ApiResponse(
        code=0,
        message="success",
        data=user_menus
    )


@router.post('/update')
async def update_menu(menu: Menu, session: Session = Depends(get_session)):
    """
    菜单的id是不可变的
    更新：从id开始选择对应的menu信息，然后更新
    添加：无id字段，则表示为新添加的菜单
    :param menuInfo:
    :param session:
    :return:
    """
    if menu.id:
        # 存在菜单id，则为更新
        sql = select(Menu).where(Menu.id == menu.id)
        result = session.exec(sql).one()
        print(result)
        # menu_data = menu.dict(exclude_unset=True)
        # for key, value in menu_data.items():
        #     setattr(result, key, value)
        result = utils.update_model(result, menu)
        session.add(result)
    else:
        session.add(menu)
    session.commit()
    return ApiResponse(
        code=0,
        message="success"
    )


@router.get('/del/{id}')
async def del_menu(id: int, session: Session = Depends(get_session)):
    sql = select(Menu).where(Menu.id == id)
    result = session.exec(sql).one()
    session.delete(result)
    session.commit()
    return ApiResponse(
        code=0,
        message="success"
    )
