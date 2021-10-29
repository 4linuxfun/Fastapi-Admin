from typing import Optional
from fastapi import Header, HTTPException, Depends, Request
from .common.security import token_decode
from jose.exceptions import JWTError, ExpiredSignatureError
from sqlmodel import Session
from .sql.database import engine


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
    if 'admin' in roles:
        print('admin roles')
