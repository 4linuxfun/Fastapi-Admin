from typing import Optional, List
from sqlmodel import Session, select
from sqlalchemy.exc import NoResultFound
from fastapi import APIRouter, Depends, status, HTTPException
from ...settings import casbin_enforcer
from ...common.response_code import ApiResponse
from ...common.auth_casbin import Authority
from ...common.database import get_session
from ...models.internal import User, Role
from ...models.internal.user import UserCreateWithRoles, UserReadWithRoles, UserUpdateWithRoles, UserUpdatePassword, \
    UserWithOutPasswd
from ...schemas.internal.pagination import Pagination
from ... import crud

router = APIRouter(prefix='/api', )


@router.get('/users/roles', summary='获取角色')
async def get_roles(id: Optional[int] = None, session: Session = Depends(get_session)):
    if id is None:
        # 添加新用户时无用户id
        roles = []
    else:
        user = crud.internal.user.get(session, id)
        roles: List[int] = [role.id for role in user.roles]
    all_roles: List[Role] = session.exec(select(Role)).all()
    # roles_list = [role.name for role in all_roles]
    return ApiResponse(
        data={
            'roles': all_roles,
            'enable': roles
        }
    )


@router.get('/users/exist', summary='用户是否存在', status_code=status.HTTP_204_NO_CONTENT)
async def check_uname_exist(name: str, session: Session = Depends(get_session)):
    try:
        crud.internal.user.check_name(session, name)
    except NoResultFound:
        return
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='用户名已存在')


@router.get('/users/{uid}',
            summary='获取用户信息', response_model=ApiResponse[UserReadWithRoles])
async def get_user_info(uid: int, session: Session = Depends(get_session)):
    try:
        user = crud.internal.user.get(session, uid)
    except NoResultFound:
        ApiResponse(code=status.HTTP_400_BAD_REQUEST, message='用户不存在')
    else:
        return ApiResponse(
            data=user
        )


@router.post('/users/search', summary="获取用户列表")
async def get_all_user(search: Pagination[UserWithOutPasswd],
                       session: Session = Depends(get_session)):
    """
    获取“用户管理”页面的用户列表清单
    :param search: Pagination实例，包含搜索的所有参数 偏移页面
    :param session:
    :return:
    """
    total = crud.internal.user.search_total(session, search.search, {'name': 'like', 'enable': 'bool'})
    print(total)
    users = crud.internal.user.search(session, search, {'name': 'like', 'enable': 'bool'})
    users_list = [user.dict(exclude={"password"}) for user in users]
    print(users_list)
    return ApiResponse(
        data={
            'total': total,
            'data': users_list
        }
    )


@router.post('/users', summary="新建用户", dependencies=[Depends(Authority("user:add"))])
async def update_user(user_info: UserCreateWithRoles, session: Session = Depends(get_session)):
    """
    更新用户信息的所有操作，可涉及更新用户名、密码、角色等
    :param user_info:
    :param session:
    :return:
    """
    print(user_info)
    user: User = crud.internal.user.insert(session, user_info)
    new_roles = [role.id for role in user.roles]
    for role in new_roles:
        casbin_enforcer.add_role_for_user(f'uid_{user.id}', f'role_{role}')
    return user


@router.put('/users/password', summary='重置密码', dependencies=[Depends(Authority('user:reset'))])
async def update_password(user: UserUpdatePassword, session: Session = Depends(get_session)):
    crud.internal.user.update_passwd(session, uid=user.id, passwd=user.password)
    return ApiResponse()


@router.put('/users/{uid}',
            summary='更新用户', dependencies=[Depends(Authority("user:update"))])
async def update_user(uid: int, user_info: UserUpdateWithRoles, session: Session = Depends(get_session)):
    """
    更新用户信息的所有操作，可涉及更新用户名、密码、角色等
    :param uid:
    :param user_info:
    :param session:
    :return:
    """
    print(user_info.dict(exclude_unset=True, exclude_none=True))
    user = crud.internal.user.update(session, uid, user_info)
    new_roles = [role.id for role in user.roles]
    casbin_enforcer.delete_roles_for_user(f'uid_{user.id}')
    for role in new_roles:
        casbin_enforcer.add_role_for_user(f'uid_{user.id}', f'role_{role}')
    return ApiResponse()


@router.delete('/users/{uid}', summary='删除用户', dependencies=[Depends(Authority("user:del"))])
async def delete_user(uid: int, session: Session = Depends(get_session)):
    try:
        user = session.exec(select(User).where(User.id == uid)).one()
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='此用户不存在')
    casbin_enforcer.delete_roles_for_user(f'uid_{user.id}')
    session.delete(user)
    session.commit()
    return ApiResponse()
