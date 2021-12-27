from typing import Set, List
from fastapi import APIRouter, Depends
from ..dependencies import get_session, check_token
from pydantic import BaseModel
from sqlmodel import Session, select
from sqlalchemy.exc import NoResultFound
from ..common.security import create_access_token
from ..sql.models import User, Menu
from ..sql.schemas import ApiResponse
from ..sql import crud
from ..common.utils import menu_convert


class UserLogin(BaseModel):
    username: str
    password: str


router = APIRouter(prefix='/api')


@router.post('/login', description="用户登录验证模块")
async def login(login_form: UserLogin, session: Session = Depends(get_session)):
    """
    处理登录请求，返回{token:xxxxx}，判断用户密码是否正确
    :param login_form:
    :param session
    :return:
    """
    try:
        sql = select(User).where(User.name == login_form.username, User.password == login_form.password,
                                 User.enable == 1)
        user: User = session.exec(sql).one()
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
    return ApiResponse(
        code=0,
        message='success',
        data={
            "uid": user.id,
            "token": access_token}
    )


@router.get('/permission', description='获取用户角色对应的菜单列表')
async def get_permission(session: Session = Depends(get_session), token: dict = Depends(check_token)):
    """
    用户权限请求，返回拥有权限的菜单列表，前端根据返回的菜单列表信息，合成菜单项
    :param session:
    :param token:
    :return:
    """
    uid: List[int] = token['uid']
    print(f"uid is:{uid}")
    user: User = session.exec(select(User).where(User.id == uid)).one()
    print(user.roles)
    user_menus = []
    for role in user.roles:
        user_menus.extend([menu.id for menu in role.menus])
    menu_list = session.exec(select(Menu).where(Menu.id.in_(set(user_menus)))).all()
    print('menulist')
    print(menu_list)
    user_menus = menu_convert(menu_list)

    print(user_menus)
    return ApiResponse(
        code=0,
        message="success",
        data=user_menus
    )
