from typing import List
from fastapi import APIRouter, Depends, Request, status
from ...common.database import get_session
from sqlmodel import Session, select
from sqlalchemy.exc import NoResultFound
from ...common.response_code import ApiResponse
from ...common.security import create_access_token
from ...models.internal import User, Menu
from ...models.internal.user import UserLogin, LoginResponse
from ... import crud
from ...common.utils import menu_convert

router = APIRouter(prefix='/api')


@router.post('/login', summary="登录验证", response_model=ApiResponse[LoginResponse])
async def login(login_form: UserLogin, session: Session = Depends(get_session)):
    """
    处理登录请求，返回{token:xxxxx}，判断用户密码是否正确
    :param login_form:
    :param session
    :return:
    """
    try:
        user = crud.internal.user.login(session, login_form)
    except NoResultFound:
        return ApiResponse(
            code=status.HTTP_400_BAD_REQUEST,
            message='用户名或密码错误',
        )
    user_roles = []
    for role in user.roles:
        if role.enable == 1:
            user_roles.append(role.id)
    # 把roles封装再token里，每次只需要depends检查对应的roles是否有权限即可
    access_token = create_access_token(
        data={"uid": user.id}
    )
    return ApiResponse(
        data={"uid": user.id,
              "token": access_token}
    )


@router.get('/permission', summary='获取权限')
async def get_permission(request: Request, session: Session = Depends(get_session)):
    """
    用户权限请求，返回拥有权限的菜单列表，前端根据返回的菜单列表信息，合成菜单项
    :param request:
    :param session:
    :param token:
    :return:
    """
    uid: int = request.state.uid
    print(f"uid is:{uid}")
    user: User = crud.internal.user.get(session, uid)
    print(user.roles)
    user_menus = []
    # admin组用户获取所有菜单列表
    if uid == 1 or crud.internal.role.check_admin(session, uid):
        menu_list = session.exec(select(Menu).where(Menu.type != 'btn').order_by(Menu.sort)).all()
        btn_list = session.exec(select(Menu.auth).where(Menu.type == 'btn').where(Menu.auth.is_not(None))).all()
    else:
        for role in user.roles:
            user_menus.extend([menu.id for menu in role.menus])
        menu_list = session.exec(
            select(Menu).where(Menu.id.in_(set(user_menus))).where(Menu.type != 'btn').order_by(Menu.sort)).all()
        btn_list = session.exec(select(Menu.auth).where(Menu.id.in_(set(user_menus))).where(Menu.type == 'btn')).all()
    print('menulist')
    print(menu_list)
    user_menus = menu_convert(menu_list)

    print(user_menus)
    return ApiResponse(
        data={
            'menus': user_menus,
            'btns': btn_list
        }
    )
