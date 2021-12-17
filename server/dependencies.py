from typing import List
from fastapi import Header, HTTPException, Depends, Request
from .common.security import token_decode
from jose.exceptions import JWTError, ExpiredSignatureError
from sqlmodel import Session, select
from .sql.database import engine
from .sql.models import User, Role, RoleMenu, Menu, MenuApi, Api
from .sql import crud


# 数据库的dependency，用于每次请求都需要创建db连接时使用
def get_session():
    with Session(engine) as session:
        yield session


async def check_token(token: str = Header(..., alias="Authorization")):
    # 传递过来的token信息格式：Bearer token,所以需要匹配
    token = token[7:]
    try:
        token_info = token_decode(token)
    except ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except JWTError as e:
        raise HTTPException(status_code=401, detail=str(e))
    print(token_info)
    return token_info


def check_roles(token: dict = Depends(check_token)):
    """
    角色检查
    :param token:
    :return:
    """
    roles = token['roles']
    return roles


def check_permission(request: Request, roles: List[int] = Depends(check_roles),
                     session: Session = Depends(get_session)):
    print('permission check')
    print(roles)
    request_permission = f"{request.method}:{request.url.path}"
    all_apis = session.exec(select(Api)).all()
    need_permissions = [api.path for api in all_apis]
    print(need_permissions)
    if request_permission in need_permissions:
        print(f'{request_permission} 需要权限验证')
        menu_list: List[Menu] = crud.get_menu_list(session, roles=roles, enable=True)
        permissions = []
        for menu in menu_list:
            permissions.extend([api.path for api in menu.apis])
        if request_permission in permissions:
            print('拥有权限')
            return True
        else:
            print('没有权限')
            raise HTTPException(status_code=403, detail="没有权限")
