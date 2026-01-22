from loguru import logger
from fastapi import Request, HTTPException
from app.settings import casbin_enforcer


class Authority:
    def __init__(self, policy: str):
        self.policy = policy

    def __call__(self, request: Request):
        if request.state.uid == 1:
            # uid为1的都跳过，为admin用户
            return True
        model, act = self.policy.split(':')
        if not casbin_enforcer.enforce(f'uid_{request.state.uid}', model, act):
            logger.warning(f'uid_{request.state.uid} {model} {act} 没有权限')
            raise HTTPException(status_code=403, detail="没有权限")
