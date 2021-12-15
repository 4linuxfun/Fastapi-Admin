from typing import List, Optional
from fastapi import APIRouter, Depends, Form
from sqlmodel import Session, select
from ..dependencies import get_session, check_token
from ..sql.models import Menu
from ..sql import crud
from ..common import utils
from ..sql.schemas import ApiResponse

router = APIRouter(prefix='/api', dependencies=[Depends(check_token), ])


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
    :param menu:
    :param session:
    :return:
    """
    sql = select(Menu).where(Menu.id == menu.id)
    result = session.exec(sql).one()
    print(result)
    # menu_data = menu.dict(exclude_unset=True)
    # for key, value in menu_data.items():
    #     setattr(result, key, value)
    result = utils.update_model(result, menu)
    session.add(result)
    session.commit()
    return ApiResponse(
        code=0,
        message="success"
    )


@router.delete('/menus/{id}')
async def del_menu(id: int, session: Session = Depends(get_session)):
    sql = select(Menu).where(Menu.id == id)
    result = session.exec(sql).one()
    session.delete(result)
    session.commit()
    return ApiResponse(
        code=0,
        message="success"
    )
