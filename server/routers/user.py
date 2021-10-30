from fastapi import APIRouter, Depends, Form
from ..dependencies import get_session, check_token
from typing import Optional, List
from ..common.security import hash_password
from pydantic import BaseModel
from sqlmodel import Session, select
from sqlalchemy.exc import NoResultFound
from ..common.security import create_access_token
from ..common.utils import menu_convert
from ..sql import crud
from ..sql.models import User, Menu, Role
from ..sql.schemas import ApiResponse
from ..common.utils import update_model


class UserLogin(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    user: User
    roles: List[str]


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


@router.post('/update',
             description='更新用户信息')
async def update_user(user_info: UserInfo, session: Session = Depends(get_session), token: dict = Depends(check_token)):
    """
    更新用户信息的所有操作，可涉及更新用户名、密码、角色等
    :param user_info:
    :param session:
    :param token:
    :return:
    """
    print(user_info)
    if user_info.user.id is None:
        updated_user = User(name=user_info.user.name, password=user_info.user.password, enable=user_info.user.enable)
    else:
        user = session.exec(select(User).where(User.id == user_info.user.id)).one()
        updated_user = update_model(user, user_info.user)
    user_roles = session.exec(select(Role).where(Role.name.in_(user_info.roles))).all()
    updated_user.roles = user_roles
    session.add(updated_user)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )


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


@router.get('/all')
async def get_all_user(session: Session = Depends(get_session), token: dict = Depends(check_token)):
    """
    获取“用户管理”页面的用户列表清单
    :param session:
    :param token:
    :return:
    """
    users = session.exec(select(User))
    users_list = [user.dict(exclude={"password": True}) for user in users]
    print(users_list)
    return ApiResponse(
        code=0,
        message="success",
        data=users_list
    )


@router.get('/role_list/')
async def get_roles(id: Optional[int] = None, session: Session = Depends(get_session, ),
                    token: dict = Depends(check_token)):
    if id is None:
        # 添加新用户时无用户id
        roles = []
    else:
        user = session.exec(select(User).where(User.id == id)).one()
        roles = [role.name for role in user.roles]

    all_roles = crud.get_roles(session)
    roles_list = [role.name for role in all_roles]
    return ApiResponse(
        code=0,
        message="success",
        data={
            'roles': roles_list,
            'enable': roles
        }
    )


@router.get('/del/{user_id}')
async def delete_user(user_id: int, session: Session = Depends(get_session),
                      token: dict = Depends(check_token)):
    user = session.exec(select(User).where(User.id == user_id)).one()
    session.delete(user)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )
