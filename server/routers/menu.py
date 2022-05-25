from typing import Optional, List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from ..db import get_session
from ..models.menu import Menu, MenusWithChild, MenuWithUpdate, MenuRead
from ..common import utils
from ..schemas import ApiResponse
from .. import crud

router = APIRouter(prefix='/api')


@router.get('/menus', summary="查询菜单", response_model=List[MenusWithChild])
async def get_all_menu(q: Optional[str] = None, session: Session = Depends(get_session)):
    # 复用crud.get_menu_list,默认role为admin就是返回所有的菜单列表
    menu_list: List[Menu] = crud.menu.search(session, q)
    menu_list_apis: List[MenuRead] = []
    for menu in menu_list:
        new_menu = MenuRead(**menu.dict(), apis=menu.apis)
        menu_list_apis.append(new_menu)
    user_menus = utils.menu_convert(menu_list_apis, "all")
    return user_menus


@router.get('/menus/tree_apis', summary='获取树形菜单接口')
async def get_menu_apis(session: Session = Depends(get_session)):
    apis = crud.api.get_tree(session)
    print(apis)
    return apis


@router.post('/menus', summary="新建菜单", response_model=Menu)
async def add_menu(menu: Menu, session: Session = Depends(get_session)):
    """
    # 新建的菜单，还是没有授权给角色的，所以直接新增就行了
    :param menu:
    :param session:
    :return:
    """
    menu = crud.menu.insert(session, menu)
    return menu


@router.put('/menus', summary="更新菜单")
async def update_menu(menu: MenuWithUpdate, session: Session = Depends(get_session)):
    """
    更新菜单，涉及到原菜单对应api的更新，则需要更新对应信息
    :param menu:
    :param session:
    :return:
    """
    db_obj = crud.menu.get(session, menu.id)
    apis = crud.api.get_multi(session, menu.apis)
    delattr(menu, "apis")
    db_obj = crud.menu.update(session, db_obj, menu)
    print(apis)
    db_obj.apis = apis
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.delete('/menus/{id}', summary='删除菜单', status_code=status.HTTP_204_NO_CONTENT)
async def del_menu(id: int, session: Session = Depends(get_session)):
    crud.menu.delete(session, id)
