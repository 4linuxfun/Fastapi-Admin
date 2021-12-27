from fastapi import APIRouter, Depends, Form
from ..dependencies import get_session, check_token
from typing import Optional, List, Union
from ..common.security import hash_password
from pydantic import BaseModel
from sqlmodel import Session, select
from sqlalchemy.exc import NoResultFound
from ..common.security import create_access_token
from ..common.utils import menu_convert
from ..sql.models import User, Menu, Role, UserRole
from ..sql.schemas import ApiResponse
from ..common.utils import update_model
from ..dependencies import casbin_enforcer


class UserInfo(BaseModel):
    user: User
    roles: List[str]


router = APIRouter(prefix='/api', )


@router.get('/users/roles', )
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


@router.get('/users/{uid}',
            description='获取用户信息')
async def get_user_info(uid: int, session: Session = Depends(get_session), token: dict = Depends(check_token)):
    sql = select(User).where(User.id == uid)
    user: User = session.exec(sql).one()
    return ApiResponse(
        code=0,
        message="success",
        data=user.dict(exclude={'password': True})
    )


@router.get('/users')
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
             description='新建用户')
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
    session.flush()
    new_roles = [role.id for role in user_roles]
    for role in new_roles:
        casbin_enforcer.add_role_for_user(f'uid_{updated_user.id}', f'role_{role}')
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )


@router.put('/users/{uid}',
            description='更新用户信息')
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
    new_roles = [role.id for role in user_roles]
    casbin_enforcer.delete_roles_for_user(f'uid_{updated_user.id}')
    for role in new_roles:
        casbin_enforcer.add_role_for_user(f'uid_{updated_user.id}', f'role_{role}')
    session.add(updated_user)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )


@router.delete('/users/{uid}')
async def delete_user(uid: int, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.id == uid)).one()
    casbin_enforcer.delete_roles_for_user(f'uid_{user.id}')
    session.delete(user)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )
