from typing import Optional, List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from ...common.database import get_session
from ...common.auth_casbin import Authority
from ...models.internal.menu import MenuBase, Menu, MenusWithChild
from ...common import utils
from ... import crud
from ...settings import casbin_enforcer

router = APIRouter(prefix='/api')


@router.get('/menus', summary="查询菜单", response_model=List[MenusWithChild])
async def get_all_menu(q: Optional[str] = None, session: Session = Depends(get_session)):
    # 复用crud.get_menu_list,默认role为admin就是返回所有的菜单列表
    menu_list: List[Menu] = crud.menu.search(session, q)
    user_menus = utils.menu_convert(menu_list)
    return user_menus


@router.post('/menus', summary="新建菜单", response_model=Menu, dependencies=[Depends(Authority("menu:add"))])
async def add_menu(menu: MenuBase, session: Session = Depends(get_session)):
    """
    # 新建的菜单，还是没有授权给角色的，所以直接新增就行了
    :param menu:
    :param session:
    :return:
    """
    db_obj = crud.menu.insert(session, Menu(**menu.dict()))
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.put('/menus', summary="更新菜单", dependencies=[Depends(Authority("menu:update"))])
async def update_menu(menu: MenuBase, session: Session = Depends(get_session)):
    """
    更新菜单，涉及到原菜单对应api的更新，则需要更新对应信息
    :param menu:
    :param session:
    :return:
    """
    db_obj: Menu = crud.menu.get(session, menu.id)
    new_obj: Menu = crud.menu.update(session, db_obj, menu)
    session.add(new_obj)
    session.commit()
    session.refresh(new_obj)
    return new_obj


@router.delete('/menus/{id}', summary='删除菜单', status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(Authority("menu:del"))])
async def del_menu(id: int, session: Session = Depends(get_session)):
    db_obj = crud.menu.get(session, id)
    if len(db_obj.roles) > 0:
        roles = [role.name for role in db_obj.roles]
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{roles} 角色关联菜单，请先取消关联")
    crud.menu.delete(session, id)
