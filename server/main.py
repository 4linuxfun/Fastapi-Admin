from sqlmodel import Session
from fastapi import FastAPI, Depends
from .routers.internal import login, user, menu, roles
from .common.security import auth_check
from .settings import engine

app = FastAPI(dependencies=[Depends(auth_check)])

# 不执行check_permission的，表示不需要权限验证
app.include_router(login.router, tags=['用户登录'])
app.include_router(user.router, tags=['用户管理'])
app.include_router(menu.router, tags=['菜单管理'])
app.include_router(roles.router, tags=['角色管理'])


@app.on_event("startup")
def startup():
    """
    在此时添加openapi数据的获取，导入api表，判断有没有新接口信息需要添加进去
    :return:
    """
    print('服务启动后执行服务')
    print('API接口更新')


@app.on_event("shutdown")
def shutdown():
    print('关闭服务')
