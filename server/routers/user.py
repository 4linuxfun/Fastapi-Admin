from fastapi import APIRouter, Depends, Form
from ..dependencies import get_session, check_permission,check_token
from typing import Optional, List, Union
from ..common.security import hash_password
from pydantic import BaseModel
from sqlmodel import Session, select
from sqlalchemy.exc import NoResultFound
from ..common.security import create_access_token
from ..common.utils import menu_convert
from ..sql import crud
from ..sql.models import User, Menu, Role, UserRole
from ..sql.schemas import ApiResponse
from ..common.utils import update_model


class UserLogin(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    user: User
    roles: List[str]


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
        data={"uid": user.id,
              "roles": user_roles}
    )
    return ApiResponse(
        code=0,
        message='success',
        data={
            "uid": user.id,
            "token": access_token}
    )


@router.get('/permission', description='获取用户角色对应的菜单列表',dependencies=[Depends(check_permission), ])
async def get_permission(session: Session = Depends(get_session), token: dict = Depends(check_token)):
    """
    用户权限请求，返回拥有权限的菜单列表，前端根据返回的菜单列表信息，合成菜单项
    :param session:
    :param token:
    :return:
    """
    roles: List[int] = token['roles']
    print(f"rolse is:{roles}")
    menu_list: List[Menu] = crud.get_menu_list(session, roles=roles, enable=True)
    print('menulist')
    print(menu_list)
    user_menus = menu_convert(menu_list)

    print(user_menus)
    return ApiResponse(
        code=0,
        message="success",
        data=user_menus
    )


@router.get('/users/roles',dependencies=[Depends(check_permission), ])
async def get_roles(id: Optional[int] = None, session: Session = Depends(get_session, ),
                    token: dict = Depends(check_token)):
    if id is None:
        # 添加新用户时无用户id
        roles = []
    else:
        user = session.exec(select(User).where(User.id == id)).one()
        roles = [role.name for role in user.roles]
    all_roles = session.exec(select(Role)).all()
    # roles_list = [role.name for role in all_roles]
    return ApiResponse(
        code=0,
        message="success",
        data={
            'roles': all_roles,
            'enable': roles
        }
    )


@router.delete('/users/{uid}',dependencies=[Depends(check_permission), ])
async def delete_user(uid: int, session: Session = Depends(get_session),
                      token: dict = Depends(check_token)):
    user = session.exec(select(User).where(User.id == uid)).one()
    session.delete(user)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )


@router.get('/users/{uid}',
            description='获取用户信息',dependencies=[Depends(check_permission), ])
async def get_user_info(uid: int, session: Session = Depends(get_session), token: dict = Depends(check_token)):
    sql = select(User).where(User.id == uid)
    user: User = session.exec(sql).one()
    return ApiResponse(
        code=0,
        message="success",
        data=user.dict(exclude={'password': True})
    )


@router.put('/users/{uid}',
            description='更新用户信息',dependencies=[Depends(check_permission), ])
async def update_user(uid: int, user_info: UserInfo, session: Session = Depends(get_session),
                      token: dict = Depends(check_token)):
    """
    更新用户信息的所有操作，可涉及更新用户名、密码、角色等
    :param uid:
    :param user_info:
    :param session:
    :param token:
    :return:
    """
    print(user_info)
    user = session.exec(select(User).where(User.id == uid)).one()
    updated_user = update_model(user, user_info.user)
    user_roles = session.exec(select(Role).where(Role.name.in_(user_info.roles))).all()
    updated_user.roles = user_roles
    session.add(updated_user)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )


@router.get('/users',dependencies=[Depends(check_permission), ])
async def get_all_user(q: Optional[str] = None, session: Session = Depends(get_session),
                       token: dict = Depends(check_token)):
    """
    获取“用户管理”页面的用户列表清单
    :param q:
    :param session:
    :param token:
    :return:
    """
    sql = select(User)
    if q is not None:
        sql = sql.where(User.name.like(f'%{q}%'))
    users = session.exec(sql)
    users_list = [user.dict(exclude={"password": True}) for user in users]
    print(users_list)
    return ApiResponse(
        code=0,
        message="success",
        data=users_list
    )


@router.post('/users',
             description='新建用户',dependencies=[Depends(check_permission), ])
async def update_user(user_info: UserInfo, session: Session = Depends(get_session), token: dict = Depends(check_token)):
    """
    更新用户信息的所有操作，可涉及更新用户名、密码、角色等
    :param user_info:
    :param session:
    :param token:
    :return:
    """
    print(user_info)
    updated_user = User(name=user_info.user.name, password=user_info.user.password, enable=user_info.user.enable)
    user_roles = session.exec(select(Role).where(Role.name.in_(user_info.roles))).all()
    updated_user.roles = user_roles
    session.add(updated_user)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )
