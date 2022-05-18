from typing import List
from fastapi import APIRouter, Depends
from ..dependencies import check_token
from ..db import get_session
from sqlmodel import Session, select
from sqlalchemy.exc import NoResultFound
from ..common.security import create_access_token
from ..models import User, Menu
from ..models.user import UserLogin, LoginResponse
from ..schemas import ApiResponse
from .. import crud
from ..common.utils import menu_convert

router = APIRouter(prefix='/api')


@router.post('/login', summary="登录验证", response_model=LoginResponse)
async def login(login_form: UserLogin, session: Session = Depends(get_session)):
    """
    处理登录请求，返回{token:xxxxx}，判断用户密码是否正确
    :param login_form:
    :param session
    :return:
    """
    try:
        user = crud.user.login(session, login_form)
    except NoResultFound:
        return ApiResponse(
            code=1,
            message='error',
            data="用户密码错误，或账号已禁用"
        )
    user_roles = []
    for role in user.roles:
        if role.enable == 1:
            user_roles.append(role.id)
    # 把roles封装再token里，每次只需要depends检查对应的roles是否有权限即可
    access_token = create_access_token(
        data={"uid": user.id}
    )
    return {"uid": user.id,
            "token": access_token}


@router.get('/permission', summary='获取权限')
async def get_permission(session: Session = Depends(get_session), token: dict = Depends(check_token)):
    """
    用户权限请求，返回拥有权限的菜单列表，前端根据返回的菜单列表信息，合成菜单项
    :param session:
    :param token:
    :return:
    """
    uid: List[int] = token['uid']
    print(f"uid is:{uid}")
    user: User = crud.user.get(session, uid)
    print(user.roles)
    user_menus = []
    # admin组用户获取所有菜单列表
    if crud.role.check_admin(session, uid):
        menu_list = session.exec(select(Menu)).all()
    else:
        for role in user.roles:
            user_menus.extend([menu.id for menu in role.menus])
        menu_list = session.exec(select(Menu).where(Menu.id.in_(set(user_menus)))).all()
    print('menulist')
    print(menu_list)
    user_menus = menu_convert(menu_list)

    print(user_menus)
    return user_menus
