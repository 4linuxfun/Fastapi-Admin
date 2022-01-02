from typing import Optional
from sqlmodel import Session, select
from fastapi import APIRouter, Depends
from ..dependencies import get_session, check_token, casbin_enforcer
from ..sql.models import User, Role
from .. import crud
from ..schemas import ApiResponse
from ..schemas.user import UserInfo

router = APIRouter(prefix='/api', )


@router.get('/users/roles', )
async def get_roles(id: Optional[int] = None, session: Session = Depends(get_session, ),
                    token: dict = Depends(check_token)):
    if id is None:
        # 添加新用户时无用户id
        roles = []
    else:
        user = crud.user.get(session, id)
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
    user = crud.user.get(session, uid)
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
    users = crud.user.search(session, q)
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
    user: User = crud.user.insert(session, user_info)
    new_roles = [role.id for role in user.roles]
    for role in new_roles:
        casbin_enforcer.add_role_for_user(f'uid_{user.id}', f'role_{role}')
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
    user = crud.user.update(session, uid, user_info)
    new_roles = [role.id for role in user.roles]
    casbin_enforcer.delete_roles_for_user(f'uid_{user.id}')
    for role in new_roles:
        casbin_enforcer.add_role_for_user(f'uid_{user.id}', f'role_{role}')
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
