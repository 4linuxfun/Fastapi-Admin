from typing import Optional
from sqlmodel import Session, select
from sqlalchemy.exc import NoResultFound
from fastapi import APIRouter, Depends
from ..dependencies import casbin_enforcer
from ..db import get_session
from ..models import User, Role
from .. import crud
from ..schemas import ApiResponse
from ..schemas.user import UserInfo

router = APIRouter(prefix='/api', )


@router.get('/users/roles', summary='获取角色')
async def get_roles(id: Optional[int] = None, session: Session = Depends(get_session, )):
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


@router.get('/users/exist', summary='用户是否存在')
async def check_uname_exist(name: str, session: Session = Depends(get_session)):
    try:
        crud.user.check_name(session, name)
    except NoResultFound:
        return ApiResponse(
            code=0,
            message='success'
        )
    else:
        return ApiResponse(
            code=1,
            message='error',
            data="用户名已存在"
        )


@router.get('/users/{uid}',
            summary='获取用户信息')
async def get_user_info(uid: int, session: Session = Depends(get_session)):
    user = crud.user.get(session, uid)
    return ApiResponse(
        code=0,
        message="success",
        data=user.dict(exclude={'password'})
    )


@router.get('/users', summary="获取用户列表")
async def get_all_user(q: Optional[str] = None, direction: str = 'next', id: Optional[int] = 0,
                       limit: Optional[int] = None, offset_page: Optional[int] = None,
                       session: Session = Depends(get_session)):
    """
    获取“用户管理”页面的用户列表清单
    :param q:查询指定用户
    :param direction: 指令，next：下一页，prev：上一页,current:刷新当前页
    :param id:对应id，根据direction去判断，next时表示start_id，prev时表示end_id，current时表示start_id,理论上ID可以为任何唯一性的自增项
    :param limit: 页面显示多少个
    :param offset_page: 偏移页面
    :param session:
    :return:
    """
    total = crud.user.search_total(session, q)
    print(total)
    users = crud.user.search(session, q, direction, id, limit, offset_page)
    users_list = [user.dict(exclude={"password"}) for user in users]
    print(users_list)
    return ApiResponse(
        code=0,
        message="success",
        data={
            'total': total,
            'data': users_list
        }
    )


@router.post('/users', summary="新建用户")
async def update_user(user_info: UserInfo, session: Session = Depends(get_session)):
    """
    更新用户信息的所有操作，可涉及更新用户名、密码、角色等
    :param user_info:
    :param session:
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
            description='更新用户')
async def update_user(uid: int, user_info: UserInfo, session: Session = Depends(get_session)):
    """
    更新用户信息的所有操作，可涉及更新用户名、密码、角色等
    :param uid:
    :param user_info:
    :param session:
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


@router.delete('/users/{uid}', summary='删除用户')
async def delete_user(uid: int, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.id == uid)).one()
    casbin_enforcer.delete_roles_for_user(f'uid_{user.id}')
    session.delete(user)
    session.commit()
    return ApiResponse(
        code=0,
        message="success",
    )
