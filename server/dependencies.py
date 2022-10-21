import json
import base64
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, Depends, Request, APIRouter
from .common.security import token_decode
from jose.exceptions import JWTError, ExpiredSignatureError
from .db import engine
import casbin_sqlalchemy_adapter
import casbin


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


def check_uid(token: dict = Depends(check_token)):
    """
    角色检查
    :param token:
    :return:
    """
    uid = token['uid']
    return uid


class PermissionCheck:
    def __init__(self, enforcer):
        self.e: casbin.Enforcer = enforcer

    def __call__(self, request: Request, uid: int = Depends(check_uid)):
        print('permission check')
        request_permission = f"{request.method}:{request.url.path}"
        print(request_permission)
        if self.e.enforce(f'uid_{uid}', request.url.path, request.method):
            print('拥有权限')
            return True
        else:
            print('没有权限')
            raise HTTPException(status_code=403, detail="没有权限")


adapter = casbin_sqlalchemy_adapter.Adapter(engine)
casbin_enforcer = casbin.Enforcer('server/model.conf', adapter)

check_permission = PermissionCheck(casbin_enforcer)
