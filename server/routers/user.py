from fastapi import APIRouter, Depends, Form
from ..dependencies import get_session, check_token
from typing import Optional, List
from ..common.security import hash_password
from pydantic import BaseModel
from sqlmodel import Session
from sqlalchemy.exc import NoResultFound
from ..common.security import create_access_token
from ..common.utils import menu_convert
from ..sql import crud
from ..sql.models import User, Menu
from ..sql.schemas import ApiResponse


class UserLogin(BaseModel):
    username: str
    password: str


router = APIRouter(prefix='/api/user')


@router.post('/login', description="用户登录验证模块")
async def login(login_form: UserLogin, session: Session = Depends(get_session)):
    """
    处理登录请求，返回{token:xxxxx}，判断用户密码是否正确
    :param login_form:
    :param session
    :return:
    """
    try:
        user: User = crud.login_check(login_form.username, login_form.password, session)
    except NoResultFound:
        return ApiResponse(
            code=1,
            message='error',
            data="用户名或密码错误"
        )
    print(user)
    user_roles: List[int] = crud.get_user_roles(user.id, session)
    # 把roles封装再token里，每次只需要depends检查对应的roles是否有权限即可
    access_token = create_access_token(
        data={"username": user.name,
              "roles": user_roles}
    )
    return ApiResponse(
        code=0,
        message='success',
        data={"token": access_token}
    )


@router.get('/user_info',
            description='获取用户信息')
async def get_user_info(session: Session = Depends(get_session), token: dict = Depends(check_token)):
    username = token['username']
    user_info: User = crud.get_user_info(username, session)
    print('user info is:')
    print(user_info)
    return ApiResponse(
        code=0,
        message="success",
        data=user_info.dict(exclude={'password': True})
    )


@router.post('/add',
             description='添加用户')
async def add_user(username: str = Form(...), password: str = Form(...), disabled: Optional[bool] = Form(False)):
    hashed_password = hash_password(password)
    if user_collection.exists(username):
        return {'code': '1', 'message': '用户名已存在'}
    user_collection.user_add({"username": username, "password": hashed_password, "disabled": disabled})
    return {'code': 0, "message": "sucess"}


@router.post('/update',
             description='更新用户信息')
async def update_user():
    pass


@router.post('/change_password',
             description='修改密码')
async def update_password(password: str = Form(...), token: dict = Depends(check_token)):
    username = token['username']
    new_password = hash_password(password)
    user_collection.change_password(username, new_password)
    return {'code': 0, 'message': 'success'}


@router.post('/disabled',
             description='用户disabled参数设置，用于设置用户无效')
async def update_disable():
    pass


@router.get('/permission', description='获取用户角色对应的菜单列表')
async def get_permission(session: Session = Depends(get_session), token: dict = Depends(check_token)):
    """
    用户权限请求，返回拥有权限的菜单列表，前端根据返回的菜单列表信息，合成菜单项
    :param session:
    :param token:
    :return:
    """
    if token['username'] == 'admin':
        roles = 'admin'
    else:
        roles = token['roles']
    menu_list: List[Menu] = crud.get_menu_list(roles, session, enable=True)
    user_menus = menu_convert(menu_list)

    print(user_menus)
    return ApiResponse(
        code=0,
        message="success",
        data=user_menus
    )
